import streamlit as st

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
PawPal+ is a pet care planning assistant. Add pets and tasks, then generate a
sorted daily schedule with automatic conflict warnings.
"""
)

# --- Session state: keep one Owner alive across reruns ---------------------
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")

owner = st.session_state.owner
scheduler = Scheduler(owner)

st.divider()

# --- Add a pet ---------------------------------------------------------------
st.subheader("Add a Pet")
with st.form("add_pet_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        new_pet_name = st.text_input("Pet name")
    with col2:
        new_pet_species = st.selectbox("Species", ["dog", "cat", "other"])
    if st.form_submit_button("Add pet") and new_pet_name:
        owner.add_pet(Pet(new_pet_name, new_pet_species))
        st.success(f"Added {new_pet_name} the {new_pet_species}.")

if owner.pets:
    st.caption("Current pets: " + ", ".join(p.name for p in owner.pets))
else:
    st.info("No pets yet. Add one above.")

st.divider()

# --- Add a task ---------------------------------------------------------------
st.subheader("Add a Task")

if not owner.pets:
    st.warning("Add a pet first before scheduling tasks.")
else:
    with st.form("add_task_form", clear_on_submit=True):
        pet_name = st.selectbox("Pet", [p.name for p in owner.pets])
        description = st.text_input("Task description", value="Morning walk")
        col1, col2, col3 = st.columns(3)
        with col1:
            time_str = st.text_input("Time (HH:MM)", value="08:00")
        with col2:
            duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        with col3:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])

        if st.form_submit_button("Add task"):
            pet = owner.find_pet(pet_name)
            pet.add_task(
                Task(
                    description=description,
                    time=time_str,
                    frequency=frequency,
                    duration_minutes=int(duration),
                    priority=priority,
                )
            )
            st.success(f"Added '{description}' for {pet_name} at {time_str}.")

st.divider()

# --- Schedule ---------------------------------------------------------------
st.subheader("Today's Schedule")

filter_pet = st.selectbox("Filter by pet", ["All"] + [p.name for p in owner.pets])
show_completed = st.checkbox("Show completed tasks", value=True)

pet_filter = None if filter_pet == "All" else filter_pet
tasks = scheduler.filter_tasks(pet_name=pet_filter)
if not show_completed:
    tasks = [t for t in tasks if not t.completed]
tasks = scheduler.sort_by_time(tasks)

conflicts = scheduler.detect_conflicts()
if conflicts:
    for warning in conflicts:
        st.warning(warning)
else:
    st.success("No scheduling conflicts detected.")

if tasks:
    st.table(
        [
            {
                "Time": t.time,
                "Pet": t.pet_name,
                "Task": t.description,
                "Duration (min)": t.duration_minutes,
                "Priority": t.priority,
                "Frequency": t.frequency,
                "Done": "✅" if t.completed else "⬜",
            }
            for t in tasks
        ]
    )

    st.markdown("#### Mark a task complete")
    task_labels = [f"{t.time} — {t.pet_name}: {t.description}" for t in tasks if not t.completed]
    if task_labels:
        chosen_label = st.selectbox("Task", task_labels)
        if st.button("Mark complete"):
            chosen_index = task_labels.index(chosen_label)
            chosen_task = [t for t in tasks if not t.completed][chosen_index]
            next_task = scheduler.mark_task_complete(chosen_task)
            if next_task:
                st.success(
                    f"Marked complete. Since it recurs '{next_task.frequency}', "
                    f"a new task was scheduled for {next_task.date}."
                )
            else:
                st.success("Marked complete.")
            st.rerun()
    else:
        st.caption("No incomplete tasks to mark.")
else:
    st.info("No tasks match the current filters.")
