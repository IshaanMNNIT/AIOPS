from typing import List, Dict
from pydantic import BaseModel


class PlanStep(BaseModel):
    action: str
    params: Dict


class Plan(BaseModel):
    goal: str
    steps: List[PlanStep]
