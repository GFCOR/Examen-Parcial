from fastapi import FastAPI, HTTPException, Body
from typing import List, Dict
from domain.models import Student, Evaluation, GradeResult
from domain.services import GradeCalculator
from domain.policies import AttendancePolicy, ExtraPointsPolicy

app = FastAPI(title="CS3081 Grade Calculator")

# In-memory storage
students_db: Dict[str, Student] = {}
config_db = {
    "all_years_teachers_agree": False
}

# Domain Services
attendance_policy = AttendancePolicy()
extra_points_policy = ExtraPointsPolicy()
calculator = GradeCalculator(attendance_policy, extra_points_policy)

@app.post("/students/{student_id}", response_model=Student)
def create_student(student_id: str):
    if student_id in students_db:
        raise HTTPException(status_code=400, detail="Student already exists")
    student = Student(id=student_id)
    students_db[student_id] = student
    return student

@app.post("/students/{student_id}/evaluations", response_model=Student)
def add_evaluation(student_id: str, evaluation: Evaluation):
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    student = students_db[student_id]
    try:
        # Validate max evaluations (RNF01)
        # We append to a copy to check validity or just append and let validator run?
        # Pydantic validators run on model creation. 
        # Let's try to append.
        if len(student.evaluations) >= 10:
             raise ValueError("RNF01: Max evaluations reached")
        
        student.evaluations.append(evaluation)
        # Re-validate model to ensure consistency if needed, but manual check above is safer for list updates
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return student

@app.put("/students/{student_id}/attendance")
def update_attendance(student_id: str, has_reached_minimum: bool = Body(..., embed=True)):
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    student = students_db[student_id]
    student.has_reached_minimum_classes = has_reached_minimum
    return {"status": "updated", "has_reached_minimum_classes": has_reached_minimum}

@app.put("/config/extra-points")
def update_extra_points_config(allYearsTeachers: bool = Body(..., embed=True)):
    config_db["all_years_teachers_agree"] = allYearsTeachers
    return {"status": "updated", "allYearsTeachers": allYearsTeachers}

@app.get("/students/{student_id}/grade", response_model=GradeResult)
def get_student_grade(student_id: str):
    if student_id not in students_db:
        raise HTTPException(status_code=404, detail="Student not found")
    
    student = students_db[student_id]
    result = calculator.calculate(student, config_db["all_years_teachers_agree"])
    return result
