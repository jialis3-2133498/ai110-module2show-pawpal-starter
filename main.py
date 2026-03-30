from pawpal_system import Pet, TimeSlot, Task, Tasks, Constraint, TasksPlanner

# --- Pets ---
luna = Pet(name="Luna", breed="Golden Retriever", age=2)
mochi = Pet(name="Mochi", breed="Shiba Inu", age=4)

# --- Owner's available time slots today ---
owner = Constraint(
    owner_name="Jordan",
    time_slots=[
        TimeSlot(start="07:00", end="08:00", available=True),
        TimeSlot(start="08:00", end="09:00", available=False),  # commute
        TimeSlot(start="12:00", end="13:00", available=True),
        TimeSlot(start="15:00", end="16:00", available=True),
        TimeSlot(start="18:00", end="19:00", available=True),
    ]
)

# --- Register pets and add tasks ---
tracker = Tasks(num_pets=2, pets=[luna, mochi])

tracker.feed_pet(luna)                                                  # P1, morning
tracker.feed_pet(mochi)                                                 # P1, morning
tracker.walk_pet(luna)                                                  # P2, anytime
tracker.groom_pet(mochi)                                                # P3, afternoon
tracker.task_list.append(Task("walk", mochi, priority=2, due_time="evening"))

# --- Reasons for each task type ---
reasons = {
    "feed":  "Regular meals keep energy levels stable and prevent hunger stress.",
    "walk":  "Daily walks provide exercise and mental stimulation.",
    "groom": "Grooming prevents matting and keeps the coat and skin healthy.",
}

# --- Build and print today's schedule ---
planner = TasksPlanner(tasks=tracker, constraint=owner, task_reasons=reasons)
planner.print_plan()
