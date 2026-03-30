from dataclasses import dataclass, field


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
    task_type: str  # "walk", "feed", "groom"
    pet: Pet
    priority: int   # lower number = higher priority
    due_time: str
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def __str__(self) -> str:
        """Return priority, type, pet name, due time, and completion status."""
        status = "✓" if self.completed else " "
        return (
            f"[{status}][P{self.priority}] "
            f"{self.task_type.capitalize()} {self.pet.name} by {self.due_time}"
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

    def get_tasks_for_pet(self, pet: Pet) -> list[Task]:
        """Return all tasks assigned to the specified pet."""
        return [t for t in self.task_list if t.pet.name == pet.name]

    def get_tasks_by_priority(self) -> list[Task]:
        """Return all tasks sorted from highest to lowest priority."""
        return sorted(self.task_list, key=lambda t: t.priority)


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

    def __str__(self) -> str:
        """Return a summary of the owner's name and available time slots."""
        slots = ", ".join(str(s) for s in self.get_available_slots())
        return f"Owner: {self.owner_name} | Available: {slots or 'none'}"


@dataclass
class TasksPlanner:
    tasks: Tasks
    constraint: Constraint
    task_reasons: dict[str, str] = field(default_factory=dict)

    def explain_task(self, task: Task) -> str:
        reason = self.task_reasons.get(task.task_type, "No reason provided.")
        return f"Task '{task.task_type}' for {task.pet.name}: {reason}"

    def schedule(self) -> list[tuple[Task, TimeSlot]]:
        available_slots = self.constraint.get_available_slots()
        sorted_tasks = self.tasks.get_tasks_by_priority()

        plan: list[tuple[Task, TimeSlot]] = []
        slot_index = 0
        for task in sorted_tasks:
            if slot_index >= len(available_slots):
                break
            plan.append((task, available_slots[slot_index]))
            slot_index += 1
        return plan

    def print_plan(self) -> None:
        plan = self.schedule()
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
