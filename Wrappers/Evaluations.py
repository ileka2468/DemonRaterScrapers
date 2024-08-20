from AbstractTable import AbstractTable
from CourseHistory import CourseHistory


class Evaluations(AbstractTable):
    _table_name = "Evaluations"
    _joinable_tables = [CourseHistory]

    class Cols(AbstractTable.Cols):
        EVAL_ID = "eval_id"
        OBJECTIVES = "course_objectives"
        ASSIGNMENTS = "assignments_effective"
        PRESENTATION = "instructor_presentation"
        GRADING = "fair_grading"
        ENGAGEMENT = "instructor_engagement"
        RESPECT = "instructor_respect"
        WORKLOAD = "workload"
        ORGANIZATION = "material_organization"
        CHALLENGE = "course_challenge"
        RESPONSIVENESS = "instructor_responsiveness"
        SPEED = "grading_speed"
        RESPONSES = "responses"
        SCORE = "score"
        ADJUSTED_SCORE = "adjusted_score"

        class Foreign(AbstractTable.Cols.Foreign):
            CH_ID = ("ch_id", CourseHistory)
