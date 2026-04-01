from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str  # "low", "medium", "high"
    completed: bool = False
    notes: Optional[str] = None
    pet_name: str = ""  # set automatically when added to a Pet

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def reset(self) -> None:
        """Reset this task to incomplete for a new day."""
        self.completed = False

    def priority_value(self) -> int:
        """Return a numeric priority so tasks can be sorted (high=3, medium=2, low=1)."""
        return {"low": 1, "medium": 2, "high": 3}.get(self.priority, 0)


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet and stamp the pet's name onto it."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet's task list."""
        self.tasks.remove(task)

    def get_pending_tasks(self) -> list[Task]:
        """Return only tasks that have not been completed yet."""
        return [t for t in self.tasks if not t.completed]


class Owner:
    def __init__(self, name: str, available_minutes: int):
        self.name = name
        self.available_minutes = available_minutes
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return a flat list of every task across all owned pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner

    def generate_plan(self) -> list[Task]:
        """Select and sort pending tasks that fit within the owner's available time budget."""
        pending = [t for t in self.owner.get_all_tasks() if not t.completed]
        sorted_tasks = sorted(pending, key=lambda t: t.priority_value(), reverse=True)

        plan = []
        time_used = 0
        for task in sorted_tasks:
            if time_used + task.duration_minutes <= self.owner.available_minutes:
                plan.append(task)
                time_used += task.duration_minutes

        return plan

    def explain_plan(self, plan: list[Task]) -> str:
        """Return a human-readable summary of the plan, including skipped tasks."""
        if not plan:
            return "No tasks could be scheduled — either there are no pending tasks or there isn't enough time."

        all_pending = [t for t in self.owner.get_all_tasks() if not t.completed]
        skipped = [t for t in all_pending if t not in plan]

        lines = [f"Plan for {self.owner.name} ({self.owner.available_minutes} minutes available):\n"]
        time_used = 0
        for task in plan:
            label = f"{task.pet_name}'s {task.title}" if task.pet_name else task.title
            lines.append(f"  - {label} ({task.duration_minutes} min, {task.priority} priority)")
            time_used += task.duration_minutes

        lines.append(f"\nTotal time scheduled: {time_used} / {self.owner.available_minutes} minutes.")

        if skipped:
            lines.append("\nSkipped (didn't fit in the time budget):")
            for task in skipped:
                label = f"{task.pet_name}'s {task.title}" if task.pet_name else task.title
                lines.append(f"  - {label} ({task.duration_minutes} min, {task.priority} priority)")

        return "\n".join(lines)

    def total_scheduled_time(self, plan: list[Task]) -> int:
        """Return the total duration in minutes for all tasks in the plan."""
        return sum(t.duration_minutes for t in plan)
