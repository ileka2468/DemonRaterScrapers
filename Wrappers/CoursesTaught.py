from Wrappers.AbstractTable import AbstractTable
from Wrappers.Courses import Courses
from Wrappers.Professors import Professors


class CoursesTaught(AbstractTable):
    _table_name = "Courses Taught"
    _joinable_tables = [Courses, Professors]

    class Cols(AbstractTable.Cols):
        COURSES_TAUGHT_ID = "ctghtid"

        class Foreign(AbstractTable.Cols.Foreign):
            COURSE_CODE_ID = "course_code_id"
            PROFESSOR_ID = "professor_id"

        class _Joinable(AbstractTable.Cols._Joinable):
            COURSE_CODE_ID = ("course_code_id", Courses)
            PROFESSOR_ID = ("professor_id", Professors)