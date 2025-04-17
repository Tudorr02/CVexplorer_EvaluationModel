from enum import Enum
from typing import List
from pydantic import BaseModel, Field

class PositionLevel(str, Enum):
    intern = "Intern"
    junior = "Junior"
    mid = "Mid"
    senior = "Senior"
    lead = "Lead"

class EducationLevel(str, Enum):
    highSchool = "HighSchool"
    bachelor = "Bachelor"
    master = "Master"
    doctorate = "Doctorate"

class PositionDTO(BaseModel):
    name: str = Field(..., description="Name of the position")
    requiredSkills: List[str] = []
    niceToHave: List[str] = []
    languages: List[str] = []
    certifications: List[str] = []
    responsibilities: List[str] = []
    minimumExperienceMonths: int = 0
    level: PositionLevel = PositionLevel.intern
    minimumEducationLevel: EducationLevel = EducationLevel.highSchool

class CvEvaluationRequest(BaseModel):
    cv_text: str = Field(..., description="The CV text input")
    position: PositionDTO
