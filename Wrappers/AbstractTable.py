import inspect
from itertools import chain

from supabase_client import SupaBaseClient


class AbstractTable:
    _table_name = ""  # Default value, should be overridden by subclasses
    _joinable_tables = []  # Default values for tables that this table can be joined with

    class Cols:
        ALL = "*"

    _db = SupaBaseClient.instance()

    @classmethod
    def get_all(cls, *selected_columns) -> list:
        cls._validate_columns(list(selected_columns))
        return cls._db.from_(cls._table_name).select(','.join(selected_columns) if selected_columns else cls.Cols.ALL).execute().data

    @classmethod
    def get_single_record(cls, where_map: dict, *selected_columns) -> dict | None:
        cls._validate_columns(list(selected_columns))
        assert isinstance(where_map, dict) and len(where_map) > 0, \
            "Where map must be a dictionary and have at least one key value pair"

        quoted_columns = [f'"{column}"' for column in selected_columns]
        code = f"cls._db.from_('{cls._table_name}').select({','.join(quoted_columns)}){cls._generate_equalities(where_map)}"
        if eval(code):
            return eval(code)[0]
        return None
    @classmethod
    def get_multiple_records(cls, where_map: dict, *selected_columns) -> list:
        cls._validate_columns(list(selected_columns))
        assert isinstance(where_map, dict) and len(where_map) > 0, \
            "Where map must be a dictionary and have at least one key value pair"
        quoted_columns = [f'"{column}"' for column in selected_columns]
        code = f"cls._db.from_('{cls._table_name}').select({','.join(quoted_columns)}){cls._generate_equalities(where_map)}"
        return eval(code)


    @classmethod
    def insert(cls, insert_map: dict):
        cls._db.from_(cls._table_name).insert(insert_map).execute()

    @classmethod
    def _generate_equalities(cls, dictionary: dict) -> str:
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
        members = [member_tuple[1] for member_tuple in cls._get_members()]
        for column in columns:
            if column not in members:
                for joinable_table in cls._joinable_tables:
                    joinable_members = [member_tuple[1] for member_tuple in joinable_table._get_members()]
                    if column in joinable_members:
                        break
                    else:
                        all_members = members + list(chain.from_iterable(
                            [table.get_table_name() + "." + member_tuple[1] for member_tuple in table._get_members()] for table in
                            cls._joinable_tables))
                        raise ValueError(f"Column {column} not found in this tables acceptable columns or joinable table columns: {all_members}")

    @classmethod
    def _get_members(cls):
        members = []
        for i in inspect.getmembers_static(cls.Cols):
            if not i[0].startswith('_'):
                if not inspect.ismethod(i[1]):
                    members.append(i)
        return members

    @classmethod
    def get_table_name(cls):
        return cls._table_name
