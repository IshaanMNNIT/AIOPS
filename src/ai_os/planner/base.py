from abc import ABC, abstractmethod
from ai_os.planner.plan import Plan

class BasePlanner(ABC):
    @abstractmethod
    def plan(self, goal: str) -> Plan:
        pass