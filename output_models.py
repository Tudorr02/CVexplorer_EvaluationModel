from typing import List, Optional
from pydantic import BaseModel, Field
from models import PositionLevel, EducationLevel

class SkillsResult(BaseModel):
    scraped: List[str]
    score: float

class LanguagesResult(BaseModel):
    value: List[str]
    score: float

class ExperienceResult(BaseModel):
    value: float
    score: float

class LevelResult(BaseModel):
    value: PositionLevel    # One of "Intern", "Junior", "Mid", "Senior", "Lead"
    score: float

class EducationResult(BaseModel):
    value: EducationLevel  # One of "HighScool", "Bachelor", "Master", "Doctorate"
    score: float

class CVEvaluationResultDTO(BaseModel):
    candidateName: Optional[str] = Field(default=None, description="Numele extras sau None dacă nu s-a găsit")                     # JSON will be camelCase
    requiredSkills:          SkillsResult
    niceToHave:              SkillsResult
    languages:               LanguagesResult
    certifications:          SkillsResult
    responsibilities:        SkillsResult
    minimumExperienceMonths: ExperienceResult
    level:                   LevelResult
    minimumEducationLevel:   EducationResult
