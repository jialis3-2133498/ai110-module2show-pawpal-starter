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

# --- Register pets and add tasks OUT OF ORDER (low priority first) ---
tracker = Tasks(num_pets=2, pets=[luna, mochi])

tracker.groom_pet(mochi)                                                # P3, afternoon  (added first)
tracker.task_list.append(Task("walk", mochi, priority=2, due_time="evening"))  # P2, evening
tracker.walk_pet(luna)                                                  # P2, anytime
tracker.feed_pet(mochi)                                                 # P1, morning
tracker.feed_pet(luna)                                                  # P1, morning   (added last)

# Set recurrence on the feed tasks so they auto-spawn next occurrences
tracker.task_list[3].recurrence = "daily"   # Feed Mochi -> daily
tracker.task_list[4].recurrence = "daily"   # Feed Luna  -> daily
tracker.task_list[0].recurrence = "weekly"  # Groom Mochi -> weekly

# --- Sorting Demo ---
print("=" * 50)
print("ALL TASKS (insertion order):")
for t in tracker.task_list:
    print(f"  {t}")

print("\nSORTED BY PRIORITY + TIME:")
for t in tracker.get_tasks_by_priority():
    print(f"  {t}")

# --- Filtering Demo ---
print("\nFILTER — pending tasks only:")
for t in tracker.filter_tasks(completed=False):
    print(f"  {t}")

print("\nFILTER — all tasks for Luna:")
for t in tracker.filter_tasks(pet_name="Luna"):
    print(f"  {t}")

print("\nFILTER — pending tasks for Mochi:")
for t in tracker.filter_tasks(pet_name="Mochi", completed=False):
    print(f"  {t}")

# --- Recurring Task Demo ---
print("\n" + "=" * 50)
print("RECURRING TASK DEMO")
print("Completing today's feed (daily) and groom (weekly) tasks...\n")

feed_mochi = tracker.task_list[3]
feed_luna  = tracker.task_list[4]
groom_mochi = tracker.task_list[0]

next_feed_mochi  = tracker.complete_task(feed_mochi)
next_feed_luna   = tracker.complete_task(feed_luna)
next_groom_mochi = tracker.complete_task(groom_mochi)

print(f"  Completed : {feed_mochi}")
print(f"  Spawned   : {next_feed_mochi}\n")
print(f"  Completed : {feed_luna}")
print(f"  Spawned   : {next_feed_luna}\n")
print(f"  Completed : {groom_mochi}")
print(f"  Spawned   : {next_groom_mochi}\n")

print("ALL TASKS AFTER COMPLETION (pending only):")
for t in tracker.filter_tasks(completed=False):
    print(f"  {t}")

# --- Build and print today's schedule ---
print("\n" + "=" * 50)
reasons = {
    "feed":  "Regular meals keep energy levels stable and prevent hunger stress.",
    "walk":  "Daily walks provide exercise and mental stimulation.",
    "groom": "Grooming prevents matting and keeps the coat and skin healthy.",
}
planner = TasksPlanner(tasks=tracker, constraint=owner, task_reasons=reasons)
planner.print_plan()

# --- Conflict Detection Demo ---
# Two available slots intentionally overlap (08:00-10:00 and 09:00-11:00),
# so both a walk and a feed task land in overlapping windows.
print("\n" + "=" * 50)
print("CONFLICT DETECTION DEMO")
print("(Two overlapping slots: 08:00-10:00 and 09:00-11:00)\n")

conflict_owner = Constraint(
    owner_name="Jordan",
    time_slots=[
        TimeSlot(start="08:00", end="10:00", available=True),  # overlaps with next slot
        TimeSlot(start="09:00", end="11:00", available=True),  # overlaps with previous slot
        TimeSlot(start="14:00", end="15:00", available=True),
    ]
)

conflict_tracker = Tasks(num_pets=2, pets=[luna, mochi])
conflict_tracker.feed_pet(luna)    # P1 — assigned to 08:00-10:00
conflict_tracker.walk_pet(mochi)   # P2 — assigned to 09:00-11:00 (overlaps!)
conflict_tracker.groom_pet(luna)   # P3 — assigned to 14:00-15:00

conflict_planner = TasksPlanner(
    tasks=conflict_tracker,
    constraint=conflict_owner,
    task_reasons=reasons,
)
conflict_planner.print_plan()
