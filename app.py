import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# --- Session State Initialization ---
# st.session_state works like a dictionary that survives reruns.
# The "not in" check means: only create the object the very first time —
# after that, Streamlit reuses whatever is already stored there.
if "owner" not in st.session_state:
    st.session_state.owner = None

if "scheduler" not in st.session_state:
    st.session_state.scheduler = None

# -------------------------------------------------------
# SECTION 1: Owner Setup
# -------------------------------------------------------
st.subheader("Owner Info")

with st.form("owner_form"):
    owner_name = st.text_input("Your name", value="Jordan")
    available_minutes = st.number_input("Minutes available today", min_value=10, max_value=480, value=90)
    submitted = st.form_submit_button("Save Owner")

if submitted:
    # Create a new Owner and store it in session_state so it persists across reruns
    st.session_state.owner = Owner(name=owner_name, available_minutes=available_minutes)
    st.session_state.scheduler = Scheduler(owner=st.session_state.owner)
    st.success(f"Owner '{owner_name}' saved with {available_minutes} minutes available.")

if st.session_state.owner is None:
    st.info("Fill in your info above to get started.")
    st.stop()

owner = st.session_state.owner

# -------------------------------------------------------
# SECTION 2: Add a Pet
# -------------------------------------------------------
st.divider()
st.subheader("Add a Pet")

with st.form("pet_form"):
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "rabbit", "other"])
    age = st.number_input("Age", min_value=0, max_value=30, value=3)
    add_pet = st.form_submit_button("Add Pet")

if add_pet:
    new_pet = Pet(name=pet_name, species=species, age=age)
    owner.add_pet(new_pet)  # <-- Owner.add_pet() stores the Pet in owner.pets
    st.success(f"Added {pet_name} the {species}!")

if owner.pets:
    st.write("**Your pets:**", ", ".join(p.name for p in owner.pets))
else:
    st.info("No pets added yet.")

# -------------------------------------------------------
# SECTION 3: Add a Task to a Pet
# -------------------------------------------------------
st.divider()
st.subheader("Add a Task")

if not owner.pets:
    st.warning("Add a pet first before adding tasks.")
else:
    with st.form("task_form"):
        pet_choice = st.selectbox("Which pet?", [p.name for p in owner.pets])
        task_title = st.text_input("Task title", value="Morning walk")
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        notes = st.text_input("Notes (optional)", value="")
        add_task = st.form_submit_button("Add Task")

    if add_task:
        # Find the selected Pet object, then call Pet.add_task()
        selected_pet = next(p for p in owner.pets if p.name == pet_choice)
        new_task = Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
            notes=notes or None,
        )
        selected_pet.add_task(new_task)  # <-- Pet.add_task() stamps pet_name and appends
        st.success(f"Added '{task_title}' to {pet_choice}.")

    # Show all current tasks across all pets
    all_tasks = owner.get_all_tasks()
    if all_tasks:
        st.write("**All tasks:**")
        st.table([
            {
                "Pet": t.pet_name,
                "Task": t.title,
                "Duration (min)": t.duration_minutes,
                "Priority": t.priority,
                "Done": t.completed,
            }
            for t in all_tasks
        ])

# -------------------------------------------------------
# SECTION 4: Generate Schedule
# -------------------------------------------------------
st.divider()
st.subheader("Generate Today's Schedule")

if st.button("Build Schedule"):
    scheduler = st.session_state.scheduler
    plan = scheduler.generate_plan()   # <-- Scheduler.generate_plan() filters + sorts tasks
    explanation = scheduler.explain_plan(plan)  # <-- Scheduler.explain_plan() builds the summary
    st.text(explanation)
