from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

jordan = Owner(name="Jordan", available_minutes=120)

mochi = Pet(name="Mochi", species="dog", age=3)
luna  = Pet(name="Luna",  species="cat", age=5)
jordan.add_pet(mochi)
jordan.add_pet(luna)

today = date.today()

# Intentional conflicts:
#   Morning walk  08:00 + 30 min = ends 08:30
#   Brush teeth   08:15 + 10 min = ends 08:25  <-- overlaps walk
#   Medication    08:20 +  5 min = ends 08:25  <-- also overlaps walk
#   Playtime      11:00 + 15 min = ends 11:15  <-- no conflict
#   Grooming      10:50 + 25 min = ends 11:15  <-- overlaps playtime

mochi.add_task(Task(title="Morning walk",     duration_minutes=30, priority="high",   preferred_time="08:00", frequency="daily",  due_date=today))
mochi.add_task(Task(title="Brush teeth",      duration_minutes=10, priority="medium", preferred_time="08:15", frequency="daily",  due_date=today))
luna.add_task( Task(title="Medication",       duration_minutes=5,  priority="high",   preferred_time="08:20", frequency="daily",  due_date=today, notes="One pill with food"))
luna.add_task( Task(title="Playtime",         duration_minutes=15, priority="medium", preferred_time="11:00", frequency="once",   due_date=today))
luna.add_task( Task(title="Grooming",         duration_minutes=25, priority="low",    preferred_time="10:50", frequency="weekly", due_date=today))
mochi.add_task(Task(title="Training session", duration_minutes=20, priority="low",    preferred_time="15:00", frequency="weekly", due_date=today))

scheduler = Scheduler(owner=jordan)
plan = scheduler.generate_plan()

print("=" * 50)
print("  TODAY'S SCHEDULE")
print("=" * 50)
print(scheduler.explain_plan(plan))

print()
print("=" * 50)
print("  CONFLICT CHECK")
print("=" * 50)
conflicts = scheduler.detect_conflicts(plan)
if conflicts:
    for warning in conflicts:
        print(warning)
else:
    print("  No conflicts detected.")
