from AbstractTable import AbstractTable


class Terms(AbstractTable):
    _table_name = "Terms"
    _joinable_tables = []

    class Cols(AbstractTable.Cols):
        TERM_ID = "term_id"
        TERM = "term"

        class Foreign(AbstractTable.Cols.Foreign):
            pass

        class _Joinable(AbstractTable.Cols._Joinable):
            pass