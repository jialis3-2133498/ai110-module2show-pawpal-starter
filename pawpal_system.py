from dataclasses import dataclass, field


@dataclass
class Tasks:
    num_pets: int
    pet_names: list[str]
    task_names: list[str] = field(default_factory=list)

    def walk_pet(self, pet_name: str) -> str:
        return f"Walking {pet_name}."

    def feed_pet(self, pet_name: str) -> str:
        return f"Feeding {pet_name}."

    def groom_pet(self, pet_name: str) -> str:
        return f"Grooming {pet_name}."


@dataclass
class Constraint:
    owner_name: str
    time_schedule: list[str]

    def get_schedule(self) -> list[str]:
        return self.time_schedule

    def get_name(self) -> str:
        return self.owner_name

    def __str__(self) -> str:
        return f"Owner: {self.owner_name}, Schedule: {', '.join(self.time_schedule)}"


@dataclass
class TasksPlanner:
    tasks: Tasks
    constraint: Constraint
    task_reasons: dict[str, str] = field(default_factory=dict)

    def explain_task(self, task_name: str) -> str:
        reason = self.task_reasons.get(task_name, "No reason provided.")
        return f"Task '{task_name}': {reason}"
