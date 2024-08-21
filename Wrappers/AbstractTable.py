import inspect
import time
import logging
from itertools import chain
from httpx import RemoteProtocolError
from supabase_client import SupaBaseClient
from MemberLevelEnum import MemberLevel

# Configure the logging

FOREIGN_COLUMN_NAME_OFFSET = 0
FOREIGN_TABLE_NAME_OFFSET = 1

#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class AbstractTable:
    _table_name = ""  # Default value, should be overridden by subclasses
    _joinable_tables = []  # Default values for tables that this table can be joined with

    class Cols:
        ALL = "*"

        class Foreign:
            pass

        class _Joinable:
            pass

    _db = SupaBaseClient.instance()

    @classmethod
    def get_all(cls, *selected_columns) -> list:
        logging.debug(f"Getting all records from {cls._table_name} with columns: {selected_columns}")
        cls._validate_columns(list(selected_columns))

        def execute_query():
            return cls._db.from_(cls._table_name).select(
                ','.join(selected_columns) if selected_columns else cls.Cols.ALL
            ).execute().data

        result = cls.retry_request(execute_query, max_retries=3, delay=2)
        logging.debug(f"Retrieved records: {result}")
        return result

    @classmethod
    def get_single_record(cls, where_map: dict, *selected_columns) -> dict | None:
        logging.debug(
            f"Getting single record from {cls._table_name} with where_map: {where_map} and columns: {selected_columns}")
        cls._validate_columns(list(selected_columns))
        assert isinstance(where_map, dict) and len(where_map) > 0, \
            "Where map must be a dictionary and have at least one key value pair"

        quoted_columns = [f'"{column}"' for column in selected_columns]
        code = f"cls._db.from_('{cls._table_name}').select({','.join(quoted_columns)}){cls._generate_equalities(where_map)}"

        def execute_query():
            logging.debug(f"Executing query: {code}")
            return eval(code, {'cls': cls})

        evaled_code = cls.retry_request(execute_query, max_retries=3, delay=2)
        logging.debug(f"Retrieved record: {evaled_code}")
        if evaled_code:
            return evaled_code[0]
        return None

    @classmethod
    def is_join(cls, selected_columns):
        foreign_keys = []

        for column in selected_columns:
            for foreign_member_tuple in cls._get_members(MemberLevel.FOREIGN_MEMBERS):
                if column in foreign_member_tuple:
                    foreign_keys.append(foreign_member_tuple)

        if len(foreign_keys) > 0:
            return True, foreign_keys
        else:
            return False, []

    @classmethod
    def get_multiple_records(cls, where_map: dict, *selected_columns) -> list:
        logging.debug(
            f"Getting multiple records from {cls._table_name} with where_map: {where_map} and columns: {selected_columns}")
        cls._validate_columns(list(selected_columns))
        assert isinstance(where_map, dict) and len(where_map) > 0, \
            "Where map must be a dictionary and have at least one key value pair"

        quoted_columns = [f'"{column}"' for column in selected_columns]
        code = f"cls._db.from_('{cls._table_name}').select({','.join(quoted_columns)}){cls._generate_equalities(where_map)}"

        def execute_query():
            logging.debug(f"Executing query: {code}")
            return eval(code, {'cls': cls})

        result = cls.retry_request(execute_query, max_retries=3, delay=2)
        logging.debug(f"Retrieved records: {result}")
        return result

    @classmethod
    def insert(cls, insert_map: dict):
        logging.debug(f"Inserting into {cls._table_name} with data: {insert_map}")
        result = cls._db.from_(cls._table_name).insert(insert_map).execute()
        logging.debug(f"Insert result: {result}")

    @classmethod
    def _generate_equalities(cls, dictionary: dict) -> str:
        logging.debug(f"Generating equalities for dictionary: {dictionary}")
        code = ""
        for key, value in dictionary.items():
            code += f'.eq("{key}", {cls._value_context(value)})'
        return code + ".execute().data"

    @classmethod
    def _value_context(cls, value):
        if isinstance(value, str):
            return f"'{value}'"
        return value

    @classmethod
    def _validate_columns(cls, columns: list):
        members = [member_tuple for member_tuple in cls._get_members(MemberLevel.ALL_MEMBERS)]
        for column in columns:
            if column not in members:
                found = False
                for joinable_table in cls._joinable_tables:
                    joinable_members = [member_tuple for member_tuple in joinable_table._get_members(MemberLevel.ALL_MEMBERS)]
                    if column in joinable_members:
                        found = True
                        break
                if not found:
                    all_members = members + list(chain.from_iterable(
                        [table.get_table_name() + "." + member_tuple for member_tuple in table._get_members(MemberLevel.ALL_MEMBERS)] for table
                        in
                        cls._joinable_tables))
                    raise ValueError(
                        f"Column {column} not found in this tables acceptable columns or joinable table columns: {all_members}")

    @classmethod
    def _get_members(cls, member_level: MemberLevel) -> list:
        members = []
        if member_level in [MemberLevel.MEMBERS, MemberLevel.ALL_MEMBERS]:
            for i in inspect.getmembers_static(cls.Cols):
                if not i[0].startswith('_'):
                    if not inspect.ismethod(i[1]):
                        if not inspect.isclass(i[1]):
                            members.append(i[1])

        if member_level in [MemberLevel.FOREIGN_MEMBERS, MemberLevel.ALL_MEMBERS]:
            for i in inspect.getmembers_static(cls.Cols._Joinable):
                if not i[0].startswith('_'):
                    if not inspect.ismethod(i[1]):
                        if not inspect.isclass(i[1]):
                            members.append(i[1])
        return members

    @classmethod
    def get_table_name(cls):
        return cls._table_name

    @classmethod
    def retry_request(cls, func, max_retries=3, delay=2, *args, **kwargs):
        for attempt in range(max_retries):
            try:
                logging.debug(f"Attempt {attempt + 1} for function: {func.__name__}")
                result = func(*args, **kwargs)
                logging.debug(f"Function {func.__name__} succeeded on attempt {attempt + 1}")
                return result
            except RemoteProtocolError as e:
                logging.warning(f"Attempt {attempt + 1} failed with RemoteProtocolError: {e}")
                if attempt < max_retries - 1:
                    logging.debug(f"Retrying after {delay} seconds...")
                    time.sleep(delay)
                else:
                    logging.error(f"All {max_retries} attempts failed.")
                    raise
            except Exception as e:
                logging.error(f"Unexpected error during {func.__name__}: {e}")
                raise
