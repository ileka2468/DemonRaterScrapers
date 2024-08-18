from Wrappers.AbstractTable import AbstractTable


class Courses(AbstractTable):
    _table_name = "Courses"

    class Cols(AbstractTable.Cols):
        COURSE_ID = "course_id"
        CODE = "code"
        TITLE = "title"
        DESCRIPTION = "description"
        PREREQS = "prereqs"
        EMBEDDING = "embedding"
