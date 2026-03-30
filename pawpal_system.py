from dataclasses import dataclass, field
from datetime import date, timedelta


@dataclass
class Pet:
    name: str
    breed: str
    age: int

    def __str__(self) -> str:
        """Return a readable string with the pet's name, breed, and age."""
        return f"{self.name} ({self.breed}, {self.age} yrs)"


@dataclass
class TimeSlot:
    start: str
    end: str
    available: bool

    def __str__(self) -> str:
        """Return the time range and availability status."""
        status = "open" if self.available else "busy"
        return f"{self.start}-{self.end} [{status}]"


@dataclass
class Task:
    task_type: str        # "walk", "feed", "groom"
    pet: Pet
    priority: int         # lower number = higher priority
    due_time: str
    completed: bool = False
    recurrence: str | None = None   # "daily", "weekly", or None
    due_date: date = field(default_factory=date.today)

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def __str__(self) -> str:
        """Return priority, type, pet name, due time, completion status, and recurrence."""
        status = "✓" if self.completed else " "
        recur = f" [{self.recurrence}]" if self.recurrence else ""
        return (
            f"[{status}][P{self.priority}] "
            f"{self.task_type.capitalize()} {self.pet.name} by {self.due_time}"
            f" (due {self.due_date}){recur}"
        )


@dataclass
class Tasks:
    num_pets: int
    pets: list[Pet]
    task_list: list[Task] = field(default_factory=list)

    def __post_init__(self):
        """Validate that num_pets matches the number of Pet objects provided."""
        assert self.num_pets == len(self.pets), (
            f"num_pets ({self.num_pets}) must match "
            f"the number of pets provided ({len(self.pets)})."
        )

    def walk_pet(self, pet: Pet) -> Task:
        """Create and register a walk task for the given pet."""
        task = Task(
            task_type="walk", pet=pet, priority=2, due_time="anytime"
        )
        self.task_list.append(task)
        return task

    def feed_pet(self, pet: Pet) -> Task:
        """Create and register a feed task for the given pet."""
        task = Task(task_type="feed", pet=pet, priority=1, due_time="morning")
        self.task_list.append(task)
        return task

    def groom_pet(self, pet: Pet) -> Task:
        """Create and register a groom task for the given pet."""
        task = Task(
            task_type="groom", pet=pet, priority=3, due_time="afternoon"
        )
        self.task_list.append(task)
        return task

    def complete_task(self, task: Task) -> Task | None:
        """Mark a task complete and, if it recurs, append the next occurrence.

        Returns the newly created Task for daily/weekly tasks, or None for one-off tasks.
        """
        task.mark_complete()

        if task.recurrence == "daily":
            next_due = task.due_date + timedelta(days=1)
        elif task.recurrence == "weekly":
            next_due = task.due_date + timedelta(weeks=1)
        else:
            return None

        next_task = Task(
            task_type=task.task_type,
            pet=task.pet,
            priority=task.priority,
            due_time=task.due_time,
            recurrence=task.recurrence,
            due_date=next_due,
        )
        self.task_list.append(next_task)
        return next_task

    def get_tasks_for_pet(self, pet: Pet) -> list[Task]:
        """Return all tasks assigned to the specified pet."""
        return [t for t in self.task_list if t.pet.name == pet.name]

    def filter_tasks(self, pet_name: str | None = None, completed: bool | None = None) -> list[Task]:
        """Return tasks optionally filtered by pet name and/or completion status.

        Args:
            pet_name:  If provided, only return tasks for the pet with this name.
            completed: If True, return only completed tasks.
                       If False, return only pending tasks.
                       If None, return tasks regardless of status.
        """
        results = self.task_list
        if pet_name is not None:
            results = [t for t in results if t.pet.name == pet_name]
        if completed is not None:
            results = [t for t in results if t.completed == completed]
        return results

    def get_tasks_by_priority(self) -> list[Task]:
        """Return all tasks sorted by priority, then by due_time chronologically."""
        TIME_ORDER = {"morning": 0, "afternoon": 1, "evening": 2, "anytime": 3}
        return sorted(self.task_list, key=lambda t: (t.priority, TIME_ORDER.get(t.due_time, 99)))


@dataclass
class Constraint:
    owner_name: str
    time_slots: list[TimeSlot]

    def get_schedule(self) -> list[TimeSlot]:
        """Return all time slots regardless of availability."""
        return self.time_slots

    def get_available_slots(self) -> list[TimeSlot]:
        """Return only the time slots marked as available."""
        return [s for s in self.time_slots if s.available]

    def get_name(self) -> str:
        """Return the owner's name."""
        return self.owner_name

    def get_conflicts(self) -> list[str]:
        """Return warning strings for any overlapping available time slots.

        Slots are compared by HH:MM strings, which sort correctly lexicographically.
        Returns an empty list when no overlaps are found.
        """
        warnings = []
        available = sorted(self.get_available_slots(), key=lambda s: s.start)
        for i in range(len(available) - 1):
            current, next_slot = available[i], available[i + 1]
            if current.end > next_slot.start:
                warnings.append(
                    f"Conflict: slot {current.start}-{current.end} overlaps "
                    f"with {next_slot.start}-{next_slot.end}"
                )
        return warnings

    def __str__(self) -> str:
        """Return a summary of the owner's name and available time slots."""
        slots = ", ".join(str(s) for s in self.get_available_slots())
        return f"Owner: {self.owner_name} | Available: {slots or 'none'}"


@dataclass
class TasksPlanner:
    tasks: Tasks
    constraint: Constraint
    task_reasons: dict[str, str] = field(default_factory=dict)

    def get_conflicts(self, plan: list[tuple[Task, TimeSlot]] | None = None) -> list[str]:
        """Return warning strings for any two tasks assigned to the same time slot.

        Also surfaces overlapping slot definitions from the Constraint.
        Accepts a pre-built plan to avoid calling schedule() a second time.
        Returns an empty list when no conflicts are found.
        """
        warnings = list(self.constraint.get_conflicts())

        if plan is None:
            plan = self.schedule()
        seen: dict[str, list[str]] = {}
        for task, slot in plan:
            key = f"{slot.start}-{slot.end}"
            label = f"{task.task_type}({task.pet.name})"
            seen.setdefault(key, []).append(label)

        for slot_key, task_labels in seen.items():
            if len(task_labels) > 1:
                warnings.append(
                    f"Conflict: {' and '.join(task_labels)} both scheduled at {slot_key}"
                )

        return warnings

    def explain_task(self, task: Task) -> str:
        """Return a human-readable explanation for why a task matters.

        Looks up the task type in task_reasons. Falls back to a default
        message if no reason was provided for that task type.
        """
        reason = self.task_reasons.get(task.task_type, "No reason provided.")
        return f"Task '{task.task_type}' for {task.pet.name}: {reason}"

    def schedule(self) -> list[tuple[Task, TimeSlot]]:
        """Pair tasks with available time slots in priority order.

        Tasks are sorted by priority then due_time before assignment.
        Each task is matched to the next open slot sequentially via zip,
        which naturally drops any tasks that exceed the number of available slots.

        Returns a list of (Task, TimeSlot) pairs representing the day's plan.
        """
        return list(zip(self.tasks.get_tasks_by_priority(), self.constraint.get_available_slots()))

    def print_plan(self) -> None:
        """Print the full schedule to the console, including any conflict warnings.

        Builds the plan once and reuses it for conflict detection to avoid
        running the scheduling algorithm twice. Conflict warnings are printed
        before the schedule so the owner sees them immediately.
        """
        plan = self.schedule()
        conflicts = self.get_conflicts(plan)
        if conflicts:
            print("\n⚠  Scheduling Conflicts Detected:")
            for warning in conflicts:
                print(f"   ! {warning}")

        print(f"\n=== PawPal+ Schedule for {self.constraint.get_name()} ===")
        if not plan:
            print("No tasks could be scheduled — no available time slots.")
            return
        for task, slot in plan:
            print(f"  {slot.start}-{slot.end} | {task}")
            print(f"    -> {self.explain_task(task)}")
        unscheduled = len(self.tasks.task_list) - len(plan)
        if unscheduled > 0:
            print(
                f"\n  Warning: {unscheduled} task(s) could not be "
                "scheduled (not enough open slots)."
            )


# --- Demo ---
if __name__ == "__main__":
    buddy = Pet(name="Buddy", breed="Labrador", age=3)
    whiskers = Pet(name="Whiskers", breed="Persian Cat", age=5)

    slots = [
        TimeSlot(start="08:00", end="09:00", available=True),
        TimeSlot(start="09:00", end="10:00", available=False),
        TimeSlot(start="12:00", end="13:00", available=True),
        TimeSlot(start="17:00", end="18:00", available=True),
    ]

    owner = Constraint(owner_name="Alex", time_slots=slots)

    tracker = Tasks(num_pets=2, pets=[buddy, whiskers])
    tracker.feed_pet(buddy)
    tracker.walk_pet(buddy)
    tracker.groom_pet(whiskers)
    tracker.feed_pet(whiskers)

    reasons = {
        "feed": "Pets need consistent meal times to maintain energy.",
        "walk": "Daily walks keep dogs stimulated and physically fit.",
        "groom": "Grooming prevents matting and keeps the coat healthy.",
    }

    planner = TasksPlanner(tasks=tracker, constraint=owner, task_reasons=reasons)
    planner.print_plan()
