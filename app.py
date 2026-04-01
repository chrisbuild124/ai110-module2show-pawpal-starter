import streamlit as st
from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# --- Session State Initialization ---
if "owner" not in st.session_state:
    st.session_state.owner = None
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None

# -------------------------------------------------------
# SECTION 1: Owner Setup
# -------------------------------------------------------
st.subheader("Owner Info")

with st.form("owner_form"):
    owner_name        = st.text_input("Your name", value="Jordan")
    available_minutes = st.number_input("Minutes available today", min_value=10, max_value=480, value=90)
    submitted         = st.form_submit_button("Save Owner")

if submitted:
    st.session_state.owner     = Owner(name=owner_name, available_minutes=available_minutes)
    st.session_state.scheduler = Scheduler(owner=st.session_state.owner)
    st.success(f"Owner '{owner_name}' saved with {available_minutes} minutes available.")

if st.session_state.owner is None:
    st.info("Fill in your info above to get started.")
    st.stop()

owner     = st.session_state.owner
scheduler = st.session_state.scheduler

# -------------------------------------------------------
# SECTION 2: Add a Pet
# -------------------------------------------------------
st.divider()
st.subheader("Add a Pet")

with st.form("pet_form"):
    pet_name = st.text_input("Pet name", value="Mochi")
    species  = st.selectbox("Species", ["dog", "cat", "rabbit", "other"])
    age      = st.number_input("Age", min_value=0, max_value=30, value=3)
    add_pet  = st.form_submit_button("Add Pet")

if add_pet:
    owner.add_pet(Pet(name=pet_name, species=species, age=age))
    st.success(f"Added {pet_name} the {species}!")

if owner.pets:
    st.write("**Your pets:**", ", ".join(p.name for p in owner.pets))
else:
    st.info("No pets added yet.")

# -------------------------------------------------------
# SECTION 3: Add a Task
# -------------------------------------------------------
st.divider()
st.subheader("Add a Task")

if not owner.pets:
    st.warning("Add a pet first before adding tasks.")
else:
    with st.form("task_form"):
        pet_choice     = st.selectbox("Which pet?", [p.name for p in owner.pets])
        task_title     = st.text_input("Task title", value="Morning walk")
        duration       = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority       = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        frequency      = st.selectbox("Frequency", ["once", "daily", "weekly"])
        preferred_time = st.text_input("Preferred time (HH:MM, optional)", value="")
        notes          = st.text_input("Notes (optional)", value="")
        add_task       = st.form_submit_button("Add Task")

    if add_task:
        selected_pet = next(p for p in owner.pets if p.name == pet_choice)
        selected_pet.add_task(Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
            frequency=frequency,
            preferred_time=preferred_time.strip(),
            due_date=date.today(),
            notes=notes or None,
        ))
        st.success(f"Added '{task_title}' to {pet_choice}.")

    # Show tasks sorted by time of day
    all_tasks = owner.get_all_tasks()
    if all_tasks:
        sorted_tasks = scheduler.sort_by_time(all_tasks)
        st.write("**All tasks (sorted by time):**")
        st.table([
            {
                "Pet":           t.pet_name,
                "Time":          t.preferred_time or "—",
                "Task":          t.title,
                "Duration (min)":t.duration_minutes,
                "Priority":      t.priority,
                "Frequency":     t.frequency,
                "Done":          "✓" if t.completed else "",
            }
            for t in sorted_tasks
        ])

# -------------------------------------------------------
# SECTION 4: Generate Schedule
# -------------------------------------------------------
st.divider()
st.subheader("Today's Schedule")

if st.button("Build Schedule"):
    plan = scheduler.generate_plan()

    if not plan:
        st.warning("No tasks could be scheduled. Add some tasks or increase your available time.")
    else:
        # Conflict check — show warnings before the plan so the owner sees them first
        conflicts = scheduler.detect_conflicts(plan)
        if conflicts:
            st.error(f"⚠️ {len(conflicts)} scheduling conflict(s) detected — two or more tasks overlap in time:")
            for c in conflicts:
                st.warning(c.strip())

        # Plan table sorted by preferred_time
        sorted_plan = scheduler.sort_by_time(plan)
        st.table([
            {
                "Time":          t.preferred_time or "—",
                "Pet":           t.pet_name,
                "Task":          t.title,
                "Duration (min)":t.duration_minutes,
                "Priority":      t.priority,
            }
            for t in sorted_plan
        ])

        total = scheduler.total_scheduled_time(plan)
        st.success(f"✅ {len(plan)} task(s) scheduled — {total} of {owner.available_minutes} minutes used.")

        # Show skipped tasks if any
        pending    = [t for t in owner.get_all_tasks() if not t.completed]
        skipped    = [t for t in pending if t not in plan]
        if skipped:
            with st.expander(f"Skipped tasks ({len(skipped)}) — didn't fit in the time budget"):
                for t in skipped:
                    st.write(f"- **{t.pet_name}'s {t.title}** ({t.duration_minutes} min, {t.priority} priority)")
