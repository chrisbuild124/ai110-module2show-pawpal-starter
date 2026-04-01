from pawpal_system import Owner, Pet, Task, Scheduler

# Create owner
jordan = Owner(name="Jordan", available_minutes=90)

# Create pets
mochi = Pet(name="Mochi", species="dog", age=3)
luna = Pet(name="Luna", species="cat", age=5)

# Add tasks to Mochi
mochi.add_task(Task(title="Morning walk", duration_minutes=30, priority="high"))
mochi.add_task(Task(title="Brush teeth", duration_minutes=10, priority="medium"))
mochi.add_task(Task(title="Training session", duration_minutes=20, priority="low"))

# Add tasks to Luna
luna.add_task(Task(title="Medication", duration_minutes=5, priority="high", notes="One pill with food"))
luna.add_task(Task(title="Playtime", duration_minutes=15, priority="medium"))
luna.add_task(Task(title="Grooming", duration_minutes=25, priority="low"))

# Register pets with owner
jordan.add_pet(mochi)
jordan.add_pet(luna)

# Generate and display schedule
scheduler = Scheduler(owner=jordan)
plan = scheduler.generate_plan()

print("=" * 40)
print("        TODAY'S SCHEDULE")
print("=" * 40)
print(scheduler.explain_plan(plan))
print("=" * 40)
