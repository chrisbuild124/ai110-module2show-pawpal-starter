from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional


VALID_PRIORITIES = {"low", "medium", "high"}
VALID_FREQUENCIES = {"once", "daily", "weekly"}


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str  # "low", "medium", "high"
    completed: bool = False
    notes: Optional[str] = None
    pet_name: str = ""  # set automatically when added to a Pet
    preferred_time: str = ""  # optional "HH:MM" format, e.g. "08:00"
    frequency: str = "once"  # "once", "daily", "weekly"
    due_date: Optional[date] = None

    def __post_init__(self):
        """Validate priority and frequency on creation so bad values fail loudly."""
        if self.priority not in VALID_PRIORITIES:
            raise ValueError(f"Invalid priority '{self.priority}'. Must be one of: {VALID_PRIORITIES}")
        if self.frequency not in VALID_FREQUENCIES:
            raise ValueError(f"Invalid frequency '{self.frequency}'. Must be one of: {VALID_FREQUENCIES}")

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def reset(self) -> None:
        """Reset this task to incomplete for a new day."""
        self.completed = False

    def priority_value(self) -> int:
        """Return a numeric priority so tasks can be sorted (high=3, medium=2, low=1)."""
        return {"low": 1, "medium": 2, "high": 3}[self.priority]


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
        # Primary sort: priority (high first). Tiebreaker: shorter tasks first so more fits in the budget.
        sorted_tasks = sorted(pending, key=lambda t: (-t.priority_value(), t.duration_minutes))

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

    def complete_task(self, task: Task) -> Optional[Task]:
        """Mark a task complete and, if it recurs, schedule the next occurrence on the correct pet."""
        task.mark_complete()

        if task.frequency == "once":
            return None

        delta = timedelta(days=1) if task.frequency == "daily" else timedelta(weeks=1)
        next_due = (task.due_date or date.today()) + delta

        next_task = Task(
            title=task.title,
            duration_minutes=task.duration_minutes,
            priority=task.priority,
            notes=task.notes,
            preferred_time=task.preferred_time,
            frequency=task.frequency,
            due_date=next_due,
        )

        # Find the pet this task belongs to and add the next occurrence to it
        for pet in self.owner.pets:
            if pet.name == task.pet_name:
                pet.add_task(next_task)
                break

        return next_task

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by preferred_time (HH:MM). Tasks with no time set are placed at the end."""
        return sorted(tasks, key=lambda t: t.preferred_time if t.preferred_time else "99:99")

    def filter_tasks(self, completed: bool | None = None, pet_name: str | None = None) -> list[Task]:
        """Return tasks filtered by completion status and/or pet name. Pass None to skip that filter."""
        tasks = self.owner.get_all_tasks()
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet_name.lower() == pet_name.lower()]
        return tasks

    def detect_conflicts(self, plan: list[Task]) -> list[str]:
        """Return warning strings for any tasks whose time windows overlap. Never raises — just warns."""
        def to_minutes(hhmm: str) -> int:
            h, m = hhmm.split(":")
            return int(h) * 60 + int(m)

        # Only check tasks that have a preferred_time set
        timed = [t for t in plan if t.preferred_time]

        warnings = []
        for i, a in enumerate(timed):
            for b in timed[i + 1:]:
                a_start = to_minutes(a.preferred_time)
                a_end   = a_start + a.duration_minutes
                b_start = to_minutes(b.preferred_time)
                b_end   = b_start + b.duration_minutes

                if a_start < b_end and b_start < a_end:
                    warnings.append(
                        f"  WARNING: '{a.pet_name}'s {a.title}' ({a.preferred_time}, {a.duration_minutes} min)"
                        f" overlaps with '{b.pet_name}'s {b.title}' ({b.preferred_time}, {b.duration_minutes} min)"
                    )

        return warnings
