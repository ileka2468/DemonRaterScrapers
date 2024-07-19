from AbstractTable import AbstractTable


class Terms(AbstractTable):
    _table_name = "Terms"

    class Cols(AbstractTable.Cols):
        TERM_ID = "term_id"
        TERM = "term"
