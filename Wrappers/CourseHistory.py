from Wrappers.AbstractTable import AbstractTable
from Wrappers.Courses import Courses
from Wrappers.Terms import Terms
from Professors import Professors


class CourseHistory(AbstractTable):
    _table_name = "Course History"
    _joinable_tables = [Courses, Terms, Professors]

    class Cols(AbstractTable.Cols):
        CH_ID = "ch_id"
        CH_SECTION = "section"
        CH_START_YEAR = "start_year"
        CH_END_YEAR = "end_year"

        class Foreign(AbstractTable.Cols.Foreign):
            CH_COURSE = "course"
            CH_TERM = "term"
            CH_PROFESSOR_ID = "professor_id"

        class _Joinable(AbstractTable.Cols._Joinable):
            CH_COURSE = ("course", Courses)
            CH_TERM = ("term", Terms)
            CH_PROFESSOR_ID = ("professor_id", Professors)