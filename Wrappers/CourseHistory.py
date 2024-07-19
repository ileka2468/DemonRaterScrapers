from AbstractTable import AbstractTable
from Courses import Courses
from Terms import Terms
from Professors import Professors


class CourseHistory(AbstractTable):
    _table_name = "Course History"
    _joinable_tables = [Courses, Terms, Professors]

    class Cols(AbstractTable.Cols):
        CH_ID = "ch_id"
        CH_COURSE = "course"
        CH_SECTION = "section"
        CH_TERM = "term"
        CH_START_YEAR = "start_year"
        CH_PROFESSOR_ID = "professor_id"
        CH_END_YEAR = "end_year"
