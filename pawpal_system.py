from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional


_PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    """Represents one pet-care task with time and recurrence metadata."""

    description: str
    time: str
    frequency: str = "once"
    due_date: date = field(default_factory=date.today)
    priority: str = "medium"
    completed: bool = False
    pet_name: Optional[str] = None

    def mark_complete(self) -> None:
        """Marks the task as complete."""
        self.completed = True

    def next_occurrence(self) -> Optional["Task"]:
        """Returns the next recurring task instance, if recurrence is enabled."""
        frequency = self.frequency.lower().strip()
        if frequency == "daily":
            next_date = self.due_date + timedelta(days=1)
        elif frequency == "weekly":
            next_date = self.due_date + timedelta(weeks=1)
        else:
            return None

        return Task(
            description=self.description,
            time=self.time,
            frequency=self.frequency,
            due_date=next_date,
            priority=self.priority,
            completed=False,
            pet_name=self.pet_name,
        )

    def sort_key(self) -> tuple:
        """Returns a stable key for chronological task sorting."""
        time_obj = datetime.strptime(self.time, "%H:%M").time()
        priority_rank = _PRIORITY_RANK.get(self.priority.lower(), 99)
        return self.due_date, time_obj, priority_rank, self.description.lower()

    def to_dict(self) -> dict:
        """Converts the task into a JSON-serializable dictionary."""
        return {
            "description": self.description,
            "time": self.time,
            "frequency": self.frequency,
            "due_date": self.due_date.isoformat(),
            "priority": self.priority,
            "completed": self.completed,
            "pet_name": self.pet_name,
        }


@dataclass
class Pet:
    """Represents a pet and all tasks associated with that pet."""

    name: str
    species: str
    age: Optional[int] = None
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Adds a task to the pet's task list."""
        task.pet_name = self.name
        self.tasks.append(task)

    def get_tasks(self, include_completed: bool = True) -> List[Task]:
        """Returns tasks for this pet, optionally filtering out completed items."""
        if include_completed:
            return list(self.tasks)
        return [task for task in self.tasks if not task.completed]

    def task_count(self) -> int:
        """Returns the total number of tasks for this pet."""
        return len(self.tasks)


class Owner:
    """Represents an owner who can manage multiple pets."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.pets: Dict[str, Pet] = {}

    def add_pet(self, pet: Pet) -> None:
        """Adds a pet to the owner profile using pet name as key."""
        self.pets[pet.name] = pet

    def get_pet(self, pet_name: str) -> Optional[Pet]:
        """Returns a pet by name if present."""
        return self.pets.get(pet_name)

    def add_task_to_pet(self, pet_name: str, task: Task) -> None:
        """Adds a task to a specific pet if that pet exists."""
        pet = self.get_pet(pet_name)
        if pet is None:
            raise ValueError(f"Pet '{pet_name}' not found for owner '{self.name}'.")
        pet.add_task(task)

    def all_tasks(self, include_completed: bool = True) -> List[Task]:
        """Returns tasks across all pets."""
        tasks: List[Task] = []
        for pet in self.pets.values():
            tasks.extend(pet.get_tasks(include_completed=include_completed))
        return tasks


class Scheduler:
    """Coordinates sorting, filtering, completion, and conflict checks for tasks."""

    def __init__(self, owner: Owner) -> None:
        self.owner = owner

    def sort_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Returns tasks sorted by date, time, priority, and description."""
        task_list = tasks if tasks is not None else self.owner.all_tasks()
        return sorted(task_list, key=lambda task: task.sort_key())

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
        on_date: Optional[date] = None,
    ) -> List[Task]:
        """Returns tasks filtered by pet name, completion, and due date."""
        tasks = self.owner.all_tasks(include_completed=True)

        if pet_name:
            tasks = [task for task in tasks if task.pet_name == pet_name]
        if completed is not None:
            tasks = [task for task in tasks if task.completed == completed]
        if on_date is not None:
            tasks = [task for task in tasks if task.due_date == on_date]

        return self.sort_by_time(tasks)

    def mark_task_complete(
        self,
        pet_name: str,
        description: str,
        time: str,
        on_date: Optional[date] = None,
    ) -> Optional[Task]:
        """Marks a matching task complete and creates the next recurring instance."""
        target_date = on_date or date.today()
        pet = self.owner.get_pet(pet_name)
        if pet is None:
            raise ValueError(f"Pet '{pet_name}' not found.")

        for task in pet.tasks:
            if (
                task.description == description
                and task.time == time
                and task.due_date == target_date
                and not task.completed
            ):
                task.mark_complete()
                next_task = task.next_occurrence()
                if next_task:
                    pet.add_task(next_task)
                return next_task

        return None

    def detect_conflicts(self, tasks: Optional[List[Task]] = None) -> List[str]:
        """Finds exact time collisions and returns warning messages."""
        task_list = self.sort_by_time(tasks if tasks is not None else self.owner.all_tasks())
        seen = {}
        warnings: List[str] = []

        for task in task_list:
            key = (task.due_date, task.time)
            if key in seen:
                other = seen[key]
                warnings.append(
                    (
                        f"Conflict on {task.due_date.isoformat()} at {task.time}: "
                        f"'{other.description}' ({other.pet_name}) and "
                        f"'{task.description}' ({task.pet_name})."
                    )
                )
            else:
                seen[key] = task

        return warnings

    def todays_schedule(self) -> List[Task]:
        """Returns today's incomplete tasks in chronological order."""
        today_tasks = self.filter_tasks(on_date=date.today(), completed=False)
        return self.sort_by_time(today_tasks)
