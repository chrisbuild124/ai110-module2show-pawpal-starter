from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


def test_mark_complete_changes_status():
    task = Task(title="Morning walk", duration_minutes=30, priority="high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog", age=3)
    assert len(pet.tasks) == 0
    pet.add_task(Task(title="Feeding", duration_minutes=5, priority="high"))
    assert len(pet.tasks) == 1


# --- Sorting ---

def test_sort_by_time_returns_chronological_order():
    owner = Owner(name="Jordan", available_minutes=120)
    mochi = Pet(name="Mochi", species="dog", age=3)
    owner.add_pet(mochi)

    # Added out of order on purpose
    mochi.add_task(Task(title="Evening walk",  duration_minutes=20, priority="low",    preferred_time="17:00"))
    mochi.add_task(Task(title="Medication",    duration_minutes=5,  priority="high",   preferred_time="08:00"))
    mochi.add_task(Task(title="Afternoon play",duration_minutes=15, priority="medium", preferred_time="13:00"))

    scheduler = Scheduler(owner=owner)
    sorted_tasks = scheduler.sort_by_time(owner.get_all_tasks())
    times = [t.preferred_time for t in sorted_tasks]

    assert times == ["08:00", "13:00", "17:00"]


def test_sort_by_time_tasks_without_time_go_last():
    owner = Owner(name="Jordan", available_minutes=60)
    mochi = Pet(name="Mochi", species="dog", age=3)
    owner.add_pet(mochi)

    mochi.add_task(Task(title="Walk",     duration_minutes=30, priority="high", preferred_time="07:00"))
    mochi.add_task(Task(title="No-time",  duration_minutes=10, priority="low"))   # no preferred_time

    scheduler = Scheduler(owner=owner)
    sorted_tasks = scheduler.sort_by_time(owner.get_all_tasks())

    assert sorted_tasks[-1].title == "No-time"


# --- Recurrence ---

def test_daily_task_creates_next_occurrence_one_day_later():
    owner = Owner(name="Jordan", available_minutes=60)
    mochi = Pet(name="Mochi", species="dog", age=3)
    owner.add_pet(mochi)

    today = date.today()
    task = Task(title="Walk", duration_minutes=30, priority="high", frequency="daily", due_date=today)
    mochi.add_task(task)

    scheduler = Scheduler(owner=owner)
    next_task = scheduler.complete_task(task)

    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)


def test_once_task_does_not_create_next_occurrence():
    owner = Owner(name="Jordan", available_minutes=60)
    mochi = Pet(name="Mochi", species="dog", age=3)
    owner.add_pet(mochi)

    task = Task(title="Vet visit", duration_minutes=60, priority="high", frequency="once", due_date=date.today())
    mochi.add_task(task)

    scheduler = Scheduler(owner=owner)
    result = scheduler.complete_task(task)

    assert result is None


def test_recurring_task_added_to_correct_pet():
    owner = Owner(name="Jordan", available_minutes=120)
    mochi = Pet(name="Mochi", species="dog", age=3)
    luna  = Pet(name="Luna",  species="cat", age=5)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    today = date.today()
    task = Task(title="Medication", duration_minutes=5, priority="high", frequency="daily", due_date=today)
    luna.add_task(task)

    scheduler = Scheduler(owner=owner)
    scheduler.complete_task(task)

    # The new occurrence should be on Luna, not Mochi
    assert any(t.title == "Medication" and not t.completed for t in luna.tasks)
    assert all(t.title != "Medication" for t in mochi.tasks)


# --- Conflict detection ---

def test_overlapping_tasks_are_flagged():
    owner = Owner(name="Jordan", available_minutes=120)
    mochi = Pet(name="Mochi", species="dog", age=3)
    owner.add_pet(mochi)

    # Walk starts 08:00, lasts 30 min → ends 08:30
    # Brush teeth starts 08:15 → overlaps
    mochi.add_task(Task(title="Walk",       duration_minutes=30, priority="high",   preferred_time="08:00"))
    mochi.add_task(Task(title="Brush teeth",duration_minutes=10, priority="medium", preferred_time="08:15"))

    scheduler = Scheduler(owner=owner)
    plan = scheduler.generate_plan()
    conflicts = scheduler.detect_conflicts(plan)

    assert len(conflicts) > 0


def test_adjacent_tasks_are_not_flagged():
    owner = Owner(name="Jordan", available_minutes=120)
    mochi = Pet(name="Mochi", species="dog", age=3)
    owner.add_pet(mochi)

    # Walk ends exactly at 08:30, next task starts at 08:30 — no overlap
    mochi.add_task(Task(title="Walk",      duration_minutes=30, priority="high",   preferred_time="08:00"))
    mochi.add_task(Task(title="Breakfast", duration_minutes=10, priority="medium", preferred_time="08:30"))

    scheduler = Scheduler(owner=owner)
    plan = scheduler.generate_plan()
    conflicts = scheduler.detect_conflicts(plan)

    assert len(conflicts) == 0


def test_tasks_without_time_do_not_cause_false_conflicts():
    owner = Owner(name="Jordan", available_minutes=60)
    mochi = Pet(name="Mochi", species="dog", age=3)
    owner.add_pet(mochi)

    mochi.add_task(Task(title="Walk",    duration_minutes=30, priority="high"))  # no preferred_time
    mochi.add_task(Task(title="Feeding", duration_minutes=10, priority="medium"))  # no preferred_time

    scheduler = Scheduler(owner=owner)
    plan = scheduler.generate_plan()
    conflicts = scheduler.detect_conflicts(plan)

    assert len(conflicts) == 0
