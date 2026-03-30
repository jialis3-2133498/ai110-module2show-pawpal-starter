import streamlit as st
from pawpal_system import Pet, TimeSlot, Tasks, Constraint, TasksPlanner

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# --- Vault initialization ---
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pet" not in st.session_state:
    st.session_state.pet = None
if "tracker" not in st.session_state:
    st.session_state.tracker = None

# ------------------------------------------------------------------ #
# Section 1 — Owner                                                    #
# ------------------------------------------------------------------ #
st.subheader("1. Owner")

owner_name = st.text_input("Owner name", value="Jordan")

if st.button("Save owner"):
    slots = [
        TimeSlot(start="08:00", end="09:00", available=True),
        TimeSlot(start="12:00", end="13:00", available=True),
        TimeSlot(start="17:00", end="18:00", available=True),
    ]
    # Constraint.__init__ — stores owner name and available time slots
    st.session_state.owner = Constraint(
        owner_name=owner_name, time_slots=slots
    )

if st.session_state.owner:
    # Constraint.get_name() and Constraint.__str__()
    st.info(str(st.session_state.owner))

st.divider()

# ------------------------------------------------------------------ #
# Section 2 — Add a Pet                                                #
# ------------------------------------------------------------------ #
st.subheader("2. Add a Pet")

pet_name = st.text_input("Pet name", value="Mochi")
breed = st.text_input("Breed", value="Shiba Inu")
age = st.number_input("Age (years)", min_value=0, max_value=30, value=3)

if st.button("Add pet"):
    # Pet.__init__ — creates a new pet object
    pet = Pet(name=pet_name, breed=breed, age=age)
    st.session_state.pet = pet
    # Tasks.__init__ — registers the pet and starts an empty task list
    st.session_state.tracker = Tasks(num_pets=1, pets=[pet])
    # Pet.__str__()
    st.success(f"Pet added: {str(pet)}")

if st.session_state.pet:
    st.info(f"Current pet: {str(st.session_state.pet)}")

st.divider()

# ------------------------------------------------------------------ #
# Section 3 — Add Tasks                                                #
# ------------------------------------------------------------------ #
st.subheader("3. Add Tasks")

if st.session_state.tracker is None:
    st.warning("Add a pet first before adding tasks.")
else:
    task_type = st.selectbox("Task type", ["feed", "walk", "groom"])

    if st.button("Add task"):
        tracker = st.session_state.tracker
        pet = st.session_state.pet

        # Call the matching Tasks method — each creates a Task and appends it
        if task_type == "feed":
            task = tracker.feed_pet(pet)     # Tasks.feed_pet()
        elif task_type == "walk":
            task = tracker.walk_pet(pet)     # Tasks.walk_pet()
        else:
            task = tracker.groom_pet(pet)    # Tasks.groom_pet()

        # Task.__str__()
        st.success(f"Task added: {str(task)}")

    if st.session_state.tracker.task_list:
        st.write("Current tasks:")
        # Tasks.get_tasks_by_priority() — display sorted by priority
        sorted_tasks = st.session_state.tracker.get_tasks_by_priority()
        st.table([
            {
                "task":     t.task_type,
                "pet":      t.pet.name,
                "priority": t.priority,
                "due":      t.due_time,
                "done":     t.completed,
            }
            for t in sorted_tasks
        ])
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

# ------------------------------------------------------------------ #
# Section 4 — Generate Schedule                                        #
# ------------------------------------------------------------------ #
st.subheader("4. Generate Schedule")

if st.button("Generate schedule"):
    if st.session_state.owner is None:
        st.warning("Save an owner first.")
    elif (
        st.session_state.tracker is None
        or not st.session_state.tracker.task_list
    ):
        st.warning("Add a pet and at least one task first.")
    else:
        reasons = {
            "feed":  "Regular meals keep energy levels stable.",
            "walk":  "Daily walks provide exercise and stimulation.",
            "groom": "Grooming keeps coat and skin healthy.",
        }
        planner = TasksPlanner(
            tasks=st.session_state.tracker,
            constraint=st.session_state.owner,
            task_reasons=reasons,
        )

        # TasksPlanner.schedule() — pairs tasks with available time slots
        plan = planner.schedule()

        if not plan:
            st.warning("No available slots to schedule tasks.")
        else:
            # Constraint.get_name()
            st.success(
                f"Schedule for {st.session_state.owner.get_name()}"
            )
            for task, slot in plan:
                # TasksPlanner.explain_task() — returns reason string
                st.markdown(
                    f"**{slot.start}–{slot.end}** — "
                    f"{task.task_type.capitalize()} ({task.pet.name})"
                    f" · {planner.explain_task(task)}"
                )

            unscheduled = (
                len(st.session_state.tracker.task_list) - len(plan)
            )
            if unscheduled > 0:
                st.warning(
                    f"{unscheduled} task(s) could not be scheduled "
                    "— not enough open slots."
                )
