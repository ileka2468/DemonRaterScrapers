from Wrappers.AbstractTable import AbstractTable


class Courses(AbstractTable):
    _table_name = "Courses"
    _joinable_tables = []

    class Cols(AbstractTable.Cols):
        COURSE_ID = "course_id"
        CODE = "code"
        TITLE = "title"
        DESCRIPTION = "description"
        PREREQS = "prereqs"
        EMBEDDING = "embedding"

        class Foreign(AbstractTable.Cols.Foreign):
            pass

        class _Joinable(AbstractTable.Cols._Joinable):
            pass
