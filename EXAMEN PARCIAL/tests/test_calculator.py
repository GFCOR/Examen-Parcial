import pytest
from domain.models import Student, Evaluation
from domain.policies import AttendancePolicy, ExtraPointsPolicy
from domain.services import GradeCalculator

@pytest.fixture
def calculator():
    return GradeCalculator(AttendancePolicy(), ExtraPointsPolicy())

def test_should_return_weighted_average_when_normal_case(calculator):
    student = Student(id="1")
    student.evaluations = [
        Evaluation(score=15, weight=50),
        Evaluation(score=10, weight=50)
    ]
    # Weighted: 15*0.5 + 10*0.5 = 7.5 + 5 = 12.5
    result = calculator.calculate(student, all_years_teachers_agree=False)
    assert result.final_grade == 12.5
    assert result.attendance_penalty == 0
    assert result.extra_points == 0

def test_should_return_penalty_when_attendance_not_met(calculator):
    student = Student(id="2", has_reached_minimum_classes=False)
    student.evaluations = [
        Evaluation(score=20, weight=100)
    ]
    # Base: 20. Penalty: 20 * 0.20 = 4. Final: 16.
    result = calculator.calculate(student, all_years_teachers_agree=False)
    assert result.weighted_average == 20.0
    assert result.attendance_penalty == -4.0
    assert result.final_grade == 16.0

def test_should_return_extra_points_when_teachers_agree(calculator):
    student = Student(id="3")
    student.evaluations = [
        Evaluation(score=10, weight=100)
    ]
    # Base: 10. Extra: +1. Final: 11.
    result = calculator.calculate(student, all_years_teachers_agree=True)
    assert result.extra_points == 1.0
    assert result.final_grade == 11.0

def test_should_cap_grade_at_max_when_exceeds_20(calculator):
    student = Student(id="4")
    student.evaluations = [
        Evaluation(score=20, weight=100)
    ]
    # Base: 20. Extra: +1. Final: 21 -> Cap to 20.
    result = calculator.calculate(student, all_years_teachers_agree=True)
    assert result.final_grade == 20.0

def test_should_return_zero_when_no_evaluations(calculator):
    student = Student(id="5")
    result = calculator.calculate(student, all_years_teachers_agree=False)
    assert result.final_grade == 0.0

def test_max_evaluations_constraint():
    student = Student(id="6")
    # Add 10 evaluations - OK
    for _ in range(10):
        student.evaluations.append(Evaluation(score=10, weight=10))
    
    # Add 11th - Should fail validation if we use the model validator, 
    # but since we append to list directly in python, the pydantic validator 
    # only runs on init or assignment unless validate_assignment is True.
    # However, our API endpoint handles this check manually.
    # Let's check the API logic or model validator if we re-assign.
    
    with pytest.raises(ValueError):
        # Trigger validation by re-assigning or creating new
        Student(id="fail", evaluations=[Evaluation(score=10, weight=10)] * 11)

def test_invalid_evaluation_score():
    with pytest.raises(ValueError):
        Evaluation(score=21, weight=50)
    with pytest.raises(ValueError):
        Evaluation(score=-1, weight=50)

def test_invalid_evaluation_weight():
    with pytest.raises(ValueError):
        Evaluation(score=10, weight=101)
