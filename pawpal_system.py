from dataclasses import dataclass, field


@dataclass
class Pet:
    name: str
    breed: str
    age: int


@dataclass
class TimeSlot:
    start: str
    end: str
    available: bool


@dataclass
class Task:
    task_type: str  # "walk", "feed", "groom"
    pet: Pet
    priority: int
    due_time: str


@dataclass
class Tasks:
    num_pets: int
    pets: list[Pet]
    task_list: list[Task] = field(default_factory=list)

    def __post_init__(self):
        assert self.num_pets == len(self.pets), (
            f"num_pets ({self.num_pets}) must match the number of pets provided ({len(self.pets)})."
        )

    def walk_pet(self, pet: Pet) -> str:
        return f"Walking {pet.name}."

    def feed_pet(self, pet: Pet) -> str:
        return f"Feeding {pet.name}."

    def groom_pet(self, pet: Pet) -> str:
        return f"Grooming {pet.name}."


@dataclass
class Constraint:
    owner_name: str
    time_slots: list[TimeSlot]

    def get_schedule(self) -> list[TimeSlot]:
        return self.time_slots

    def get_name(self) -> str:
        return self.owner_name

    def __str__(self) -> str:
        slots = ", ".join(f"{s.start}-{s.end}" for s in self.time_slots if s.available)
        return f"Owner: {self.owner_name}, Available slots: {slots}"


@dataclass
class TasksPlanner:
    tasks: Tasks
    constraint: Constraint
    task_reasons: dict[str, str] = field(default_factory=dict)

    def explain_task(self, task: Task) -> str:
        reason = self.task_reasons.get(task.task_type, "No reason provided.")
        return f"Task '{task.task_type}' for {task.pet.name}: {reason}"

    def schedule(self) -> list[tuple[Task, TimeSlot]]:
        available_slots = [s for s in self.constraint.time_slots if s.available]
        sorted_tasks = sorted(self.tasks.task_list, key=lambda t: t.priority)
        return list(zip(sorted_tasks, available_slots))
