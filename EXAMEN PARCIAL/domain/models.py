from typing import List, ClassVar
from pydantic import BaseModel, Field, field_validator

class Evaluation(BaseModel):
    MIN_SCORE: ClassVar[float] = 0.0
    MAX_SCORE: ClassVar[float] = 20.0
    MIN_WEIGHT: ClassVar[float] = 0.0
    MAX_WEIGHT: ClassVar[float] = 100.0

    score: float = Field(..., ge=MIN_SCORE, le=MAX_SCORE, description="Nota de la evaluación (0-20)")
    weight: float = Field(..., ge=MIN_WEIGHT, le=MAX_WEIGHT, description="Peso de la evaluación en porcentaje (0-100)")

class Student(BaseModel):
    MAX_EVALUATIONS: ClassVar[int] = 10

    id: str
    evaluations: List[Evaluation] = Field(default_factory=list, alias="examsStudents")
    has_reached_minimum_classes: bool = Field(True, alias="hasReachedMinimumClasses")
    
    model_config = {"populate_by_name": True}

    @field_validator('evaluations')
    def check_max_evaluations(cls, v):
        if len(v) > cls.MAX_EVALUATIONS:
            raise ValueError(f'RNF01: La cantidad máxima de evaluaciones por estudiante será de {cls.MAX_EVALUATIONS}.')
        return v

class GradeResult(BaseModel):
    student_id: str
    final_grade: float
    weighted_average: float
    attendance_penalty: float
    extra_points: float
    detail: str
