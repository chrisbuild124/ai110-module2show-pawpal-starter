from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str  # "low", "medium", "high"
    completed: bool = False
    notes: Optional[str] = None

    def mark_complete(self) -> None:
        pass

    def reset(self) -> None:
        pass

    def priority_value(self) -> int:
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass

    def get_pending_tasks(self) -> list[Task]:
        pass


class Owner:
    def __init__(self, name: str, available_minutes: int):
        self.name = name
        self.available_minutes = available_minutes
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        pass

    def get_all_tasks(self) -> list[Task]:
        pass


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner

    def generate_plan(self) -> list[Task]:
        pass

    def explain_plan(self, plan: list[Task]) -> str:
        pass

    def total_scheduled_time(self, plan: list[Task]) -> int:
        pass
