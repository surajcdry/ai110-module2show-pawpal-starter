from datetime import date

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")


def owner_from_state() -> Owner:
    """Returns the persisted owner object from Streamlit session state."""
    return st.session_state.owner


def scheduler_from_state() -> Scheduler:
    """Returns a scheduler instance bound to the persisted owner."""
    return Scheduler(owner_from_state())


if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")

st.title("🐾 PawPal+")
st.caption("Smart pet care tracking with sorting, filtering, recurrence, and conflict checks.")

owner = owner_from_state()

st.subheader("Owner")
owner_name = st.text_input("Owner name", value=owner.name)
if owner_name != owner.name:
    owner.name = owner_name

st.divider()

st.subheader("Add Pet")
with st.form("add_pet_form"):
    pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    age = st.number_input("Age (optional)", min_value=0, max_value=40, value=0)
    add_pet_submit = st.form_submit_button("Add pet")

if add_pet_submit:
    cleaned_name = pet_name.strip()
    if not cleaned_name:
        st.error("Please provide a pet name.")
    else:
        owner.add_pet(Pet(name=cleaned_name, species=species, age=int(age) or None))
        st.success(f"Added pet: {cleaned_name}")

pet_names = sorted(owner.pets.keys())

st.subheader("Add Task")
if not pet_names:
    st.info("Add at least one pet before scheduling tasks.")
else:
    with st.form("add_task_form"):
        selected_pet = st.selectbox("Pet", pet_names)
        description = st.text_input("Task description", value="Morning walk")
        due_date = st.date_input("Due date", value=date.today())
        task_time = st.text_input("Time (HH:MM)", value="08:00")
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])
        priority = st.selectbox("Priority", ["high", "medium", "low"], index=1)
        add_task_submit = st.form_submit_button("Add task")

    if add_task_submit:
        try:
            task = Task(
                description=description.strip(),
                time=task_time.strip(),
                frequency=frequency,
                due_date=due_date,
                priority=priority,
            )
            task.sort_key()
            owner.add_task_to_pet(selected_pet, task)
            st.success(f"Added task for {selected_pet}: {task.description}")
        except ValueError:
            st.error("Time must use HH:MM in 24-hour format.")

st.divider()

st.subheader("Schedule View")
scheduler = scheduler_from_state()

filter_col1, filter_col2, filter_col3 = st.columns(3)
with filter_col1:
    pet_filter_options = ["All pets"] + pet_names
    pet_filter = st.selectbox("Filter by pet", pet_filter_options)
with filter_col2:
    status_filter = st.selectbox("Filter by status", ["all", "pending", "completed"])
with filter_col3:
    date_filter = st.date_input("Filter by date", value=date.today())

completed_filter = None
if status_filter == "pending":
    completed_filter = False
elif status_filter == "completed":
    completed_filter = True

filtered_tasks = scheduler.filter_tasks(
    pet_name=None if pet_filter == "All pets" else pet_filter,
    completed=completed_filter,
    on_date=date_filter,
)

if filtered_tasks:
    table_rows = [task.to_dict() for task in filtered_tasks]
    st.table(table_rows)
else:
    st.info("No tasks match the selected filters.")

warnings = scheduler.detect_conflicts(filtered_tasks)
for warning in warnings:
    st.warning(warning)

st.subheader("Mark Task Complete")
pending_tasks = scheduler.filter_tasks(completed=False)

if pending_tasks:
    task_options = {
        (
            f"{task.pet_name} | {task.due_date.isoformat()} {task.time} | "
            f"{task.description} ({task.frequency})"
        ): task
        for task in pending_tasks
    }
    selected_label = st.selectbox("Pending tasks", list(task_options.keys()))
    selected_task = task_options[selected_label]

    if st.button("Mark selected task complete"):
        next_task = scheduler.mark_task_complete(
            pet_name=selected_task.pet_name or "",
            description=selected_task.description,
            time=selected_task.time,
            on_date=selected_task.due_date,
        )
        st.success("Task marked complete.")
        if next_task:
            st.success(
                "Recurring task created for "
                f"{next_task.due_date.isoformat()} at {next_task.time}."
            )
else:
    st.info("No pending tasks available.")

st.divider()

if st.button("Show Today's Schedule"):
    today_tasks = scheduler.todays_schedule()
    if today_tasks:
        st.table([task.to_dict() for task in today_tasks])
    else:
        st.info("No pending tasks for today.")
