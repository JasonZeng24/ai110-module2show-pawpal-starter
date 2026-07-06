"""Logic layer for PawPal+: Task, Pet, Owner, and Scheduler."""

from dataclasses import dataclass, field
from datetime import date, timedelta

VALID_FREQUENCIES = ("once", "daily", "weekly")
VALID_PRIORITIES = ("low", "medium", "high")


@dataclass
class Task:
    """A single pet care activity (feeding, walk, medication, appointment, etc.)."""

    description: str
    time: str  # "HH:MM", 24-hour
    frequency: str = "once"  # "once", "daily", "weekly"
    duration_minutes: int = 15
    priority: str = "medium"  # "low", "medium", "high"
    completed: bool = False
    date: date = field(default_factory=date.today)
    pet_name: str = ""

    def mark_complete(self):
        """Flip this task's completion status to True."""
        self.completed = True

    def next_occurrence(self):
        """Return the next Task instance for a recurring task, or None for a one-off task."""
        if self.frequency == "daily":
            next_date = self.date + timedelta(days=1)
        elif self.frequency == "weekly":
            next_date = self.date + timedelta(days=7)
        else:
            return None
        return Task(
            description=self.description,
            time=self.time,
            frequency=self.frequency,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            completed=False,
            date=next_date,
            pet_name=self.pet_name,
        )


@dataclass
class Pet:
    """A pet belonging to an Owner, with its own list of care tasks."""

    name: str
    species: str = "dog"
    tasks: list = field(default_factory=list)

    def add_task(self, task: Task) -> Task:
        """Attach a task to this pet and stamp it with the pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)
        return task

    def task_count(self) -> int:
        """Return how many tasks this pet currently has."""
        return len(self.tasks)


@dataclass
class Owner:
    """A pet owner who manages one or more pets."""

    name: str
    pets: list = field(default_factory=list)

    def add_pet(self, pet: Pet) -> Pet:
        """Register a new pet under this owner."""
        self.pets.append(pet)
        return pet

    def get_all_tasks(self) -> list:
        """Return every task across every pet this owner manages."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

    def find_pet(self, pet_name: str):
        """Look up a pet by name, or return None if not found."""
        for pet in self.pets:
            if pet.name == pet_name:
                return pet
        return None


class Scheduler:
    """The "brain" that retrieves, organizes, and manages tasks across an Owner's pets."""

    def __init__(self, owner: Owner):
        self.owner = owner

    def sort_by_time(self, tasks: list = None) -> list:
        """Return tasks sorted chronologically by their "HH:MM" time attribute."""
        tasks = self.owner.get_all_tasks() if tasks is None else tasks
        return sorted(tasks, key=lambda t: t.time)

    def filter_tasks(self, pet_name: str = None, completed: bool = None) -> list:
        """Return tasks optionally narrowed by pet name and/or completion status."""
        tasks = self.owner.get_all_tasks()
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet_name == pet_name]
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        return tasks

    def get_todays_schedule(self) -> list:
        """Return today's tasks across all pets, sorted by time."""
        todays_tasks = [t for t in self.owner.get_all_tasks() if t.date == date.today()]
        return self.sort_by_time(todays_tasks)

    def detect_conflicts(self, tasks: list = None) -> list:
        """Return warning strings for any tasks that share the same date and time."""
        tasks = self.owner.get_all_tasks() if tasks is None else tasks
        grouped = {}
        for task in tasks:
            grouped.setdefault((task.date, task.time), []).append(task)

        warnings = []
        for (task_date, task_time), group in grouped.items():
            if len(group) > 1:
                names = ", ".join(f"{t.pet_name} ({t.description})" for t in group)
                warnings.append(f"⚠️ Conflict at {task_time} on {task_date}: {names}")
        return warnings

    def mark_task_complete(self, task: Task):
        """Mark a task done, auto-creating its next occurrence if it recurs."""
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task is not None:
            pet = self.owner.find_pet(task.pet_name)
            if pet is not None:
                pet.add_task(next_task)
        return next_task
