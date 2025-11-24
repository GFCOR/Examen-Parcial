class AttendancePolicy:
    PENALTY_PERCENTAGE = 0.20

    def apply(self, current_grade: float, has_reached_minimum: bool) -> float:
        """
        Applies a penalty if the student has not reached the minimum attendance.
        Rule: If not reached, deduct 20% of the grade.
        """
        if not has_reached_minimum:
            return - (current_grade * self.PENALTY_PERCENTAGE) # Returns the penalty amount (negative)
        return 0.0

class ExtraPointsPolicy:
    def __init__(self, extra_points_value: float = 1.0):
        self.extra_points_value = extra_points_value

    def apply(self, all_years_teachers_agree: bool) -> float:
        """
        Applies extra points if all teachers agree.
        """
        if all_years_teachers_agree:
            return self.extra_points_value
        return 0.0
