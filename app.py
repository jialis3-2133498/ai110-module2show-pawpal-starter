import streamlit as st
from pawpal_system import Pet, TimeSlot, Tasks, Constraint, TasksPlanner

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# --- Session state initialization ---
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pets" not in st.session_state:
    st.session_state.pets = []
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
    st.session_state.owner = Constraint(owner_name=owner_name, time_slots=slots)

if st.session_state.owner:
    owner = st.session_state.owner
    st.success(f"Owner saved: **{owner.get_name()}**")

    # Show available slots as a clean table
    available_slots = owner.get_available_slots()
    if available_slots:
        st.table([{"Start": s.start, "End": s.end} for s in available_slots])

    # Surface any overlapping slot conflicts immediately
    slot_conflicts = owner.get_slot_overlaps()
    for conflict in slot_conflicts:
        st.warning(f"⚠ Slot conflict: {conflict}")

st.divider()

# ------------------------------------------------------------------ #
# Section 2 — Add a Pet                                                #
# ------------------------------------------------------------------ #
st.subheader("2. Add a Pet")

pet_name = st.text_input("Pet name", value="Mochi")
breed = st.text_input("Breed", value="Shiba Inu")
age = st.number_input("Age (years)", min_value=0, max_value=30, value=3)

if st.button("Add pet"):
    new_pet = Pet(name=pet_name, breed=breed, age=age)
    existing_names = [p.name for p in st.session_state.pets]
    if new_pet.name in existing_names:
        st.warning(f"A pet named **{new_pet.name}** is already added.")
    else:
        st.session_state.pets.append(new_pet)
        updated_pets = st.session_state.pets
        # Reconstruct Tasks with the full updated pet list
        old_tasks = st.session_state.tracker.task_list if st.session_state.tracker else []
        st.session_state.tracker = Tasks(num_pets=len(updated_pets), pets=updated_pets)
        st.session_state.tracker.task_list = old_tasks
        st.success(f"Pet added: **{str(new_pet)}**")

if st.session_state.pets:
    st.markdown("**Registered pets:**")
    st.table([{"Name": p.name, "Breed": p.breed, "Age": p.age} for p in st.session_state.pets])

st.divider()

# ------------------------------------------------------------------ #
# Section 3 — Add Tasks                                                #
# ------------------------------------------------------------------ #
st.subheader("3. Add Tasks")

if not st.session_state.pets:
    st.warning("Add a pet first before adding tasks.")
else:
    pet_names = [p.name for p in st.session_state.pets]
    selected_pet_name = st.selectbox("Pet", pet_names)
    task_type = st.selectbox("Task type", ["feed", "walk", "groom"])

    if st.button("Add task"):
        tracker = st.session_state.tracker
        pet = next(p for p in st.session_state.pets if p.name == selected_pet_name)

        if task_type == "feed":
            task = tracker.feed_pet(pet)
        elif task_type == "walk":
            task = tracker.walk_pet(pet)
        else:
            task = tracker.groom_pet(pet)

        st.success(f"Task added: **{task.task_type.capitalize()}** for {task.pet.name} (Priority {task.priority}, {task.due_time})")

    tracker = st.session_state.tracker
    if tracker.task_list:
        # --- Filter & Sort controls ---
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            filter_pet = st.selectbox("Filter by pet", ["All"] + [p.name for p in st.session_state.pets], key="filter_pet")
        with col2:
            filter_status = st.selectbox("Filter by status", ["All", "Pending", "Completed"], key="filter_status")
        with col3:
            filter_type = st.selectbox("Filter by type", ["All", "Feed", "Walk", "Groom"], key="filter_type")
        with col4:
            sort_by = st.selectbox("Sort by", ["Priority", "Due time", "Pet name"], key="sort_by")

        # Apply filters
        pet_name_filter = None if filter_pet == "All" else filter_pet
        completed_filter = None if filter_status == "All" else (filter_status == "Completed")
        filtered = tracker.filter_tasks(pet_name=pet_name_filter, completed=completed_filter)
        if filter_type != "All":
            filtered = [t for t in filtered if t.task_type == filter_type.lower()]

        # Apply sort
        TIME_ORDER = {"morning": 0, "afternoon": 1, "evening": 2, "anytime": 3}
        if sort_by == "Priority":
            filtered = sorted(filtered, key=lambda t: (t.priority, TIME_ORDER.get(t.due_time, 99)))
        elif sort_by == "Due time":
            filtered = sorted(filtered, key=lambda t: TIME_ORDER.get(t.due_time, 99))
        elif sort_by == "Pet name":
            filtered = sorted(filtered, key=lambda t: t.pet.name)

        PRIORITY_LABEL = {1: "🔴 High", 2: "🟡 Medium", 3: "🟢 Low"}
        pending_count = sum(1 for t in tracker.task_list if not t.completed)
        completed_count = sum(1 for t in tracker.task_list if t.completed)

        st.markdown("**Tasks**")
        if not filtered:
            st.info("No tasks match the current filters.")
        else:
            for task in filtered:
                actual_idx = tracker.task_list.index(task)
                col_status, col_info, col_btn = st.columns([0.5, 5, 1.5])
                with col_status:
                    st.markdown("✅" if task.completed else "⏳")
                with col_info:
                    st.markdown(
                        f"{PRIORITY_LABEL.get(task.priority, str(task.priority))} · "
                        f"**{task.task_type.capitalize()}** for **{task.pet.name}** · "
                        f"Due: {task.due_time.capitalize()} · "
                        f"Recurrence: {task.recurrence.capitalize() if task.recurrence else '—'}"
                    )
                with col_btn:
                    if not task.completed:
                        if st.button("Mark done", key=f"complete_{actual_idx}"):
                            tracker.complete_task(task)
                            st.rerun()

        if pending_count:
            st.info(f"{pending_count} pending · {completed_count} completed")
        else:
            st.success("All tasks completed!")
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
    elif st.session_state.tracker is None or not st.session_state.tracker.task_list:
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

        plan = planner.schedule()
        conflicts = planner.get_conflicts(plan)

        # Show conflict warnings above the schedule
        if conflicts:
            for conflict in conflicts:
                st.warning(f"⚠ {conflict}")

        if not plan:
            st.warning("No available slots to schedule tasks.")
        else:
            st.success(f"Schedule generated for **{st.session_state.owner.get_name()}**")

            # Schedule as a polished table
            st.table([
                {
                    "Time Slot": f"{slot.start} – {slot.end}",
                    "Task":      task.task_type.capitalize(),
                    "Pet":       task.pet.name,
                    "Priority":  task.priority,
                    "Why":       planner.explain_task(task),
                }
                for task, slot in plan
            ])

            unscheduled = len(st.session_state.tracker.task_list) - len(plan)
            if unscheduled > 0:
                st.warning(
                    f"{unscheduled} task(s) could not be scheduled — not enough open slots."
                )
