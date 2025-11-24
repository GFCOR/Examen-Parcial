from domain.models import Student, GradeResult
from domain.policies import AttendancePolicy, ExtraPointsPolicy

class GradeCalculator:
    MAX_GRADE = 20.0
    MIN_GRADE = 0.0

    def __init__(self, attendance_policy: AttendancePolicy, extra_points_policy: ExtraPointsPolicy):
        self.attendance_policy = attendance_policy
        self.extra_points_policy = extra_points_policy

    def calculate(self, student: Student, all_years_teachers_agree: bool) -> GradeResult:
        # 1. Calculate Weighted Average
        total_weight = sum(e.weight for e in student.evaluations)
        weighted_sum = sum(e.score * (e.weight / 100) for e in student.evaluations)
        
        # Normalize if weights don't sum to 100? 
        # RF doesn't specify, but usually weights are absolute percentages.
        # If total_weight < 100, the grade is just the sum.
        # If total_weight > 100, we might have an issue, but validation should handle it.
        # Let's assume the weighted_sum is the base grade.
        
        base_grade = weighted_sum

        # 2. Apply Attendance Policy
        attendance_penalty = self.attendance_policy.apply(base_grade, student.has_reached_minimum_classes)
        
        # 3. Apply Extra Points Policy
        extra_points = self.extra_points_policy.apply(all_years_teachers_agree)

        # 4. Final Calculation
        final_grade = base_grade + attendance_penalty + extra_points
        
        # Clamp grade to 0-20 range
        final_grade = max(self.MIN_GRADE, min(self.MAX_GRADE, final_grade))

        # 5. Build Detail String
        detail = (
            f"Promedio Ponderado: {base_grade:.2f} | "
            f"Penalización Asistencia: {attendance_penalty:.2f} | "
            f"Puntos Extra: {extra_points:.2f}"
        )

        return GradeResult(
            student_id=student.id,
            final_grade=round(final_grade, 2),
            weighted_average=round(base_grade, 2),
            attendance_penalty=round(attendance_penalty, 2),
            extra_points=round(extra_points, 2),
            detail=detail
        )
