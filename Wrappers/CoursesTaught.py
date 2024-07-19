from AbstractTable import AbstractTable
from Courses import Courses
from Professors import Professors


class CoursesTaught(AbstractTable):
    _table_name = "Courses Taught"
    _joinable_tables = [Courses, Professors]

    class Cols(AbstractTable.Cols):
        COURSES_TAUGHT_ID = "ctghtid"
        COURSE_CODE_ID = "course_code_id"
        PROFESSOR_ID = "professor_id"
