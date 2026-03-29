from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any


@dataclass
class Task:
	description: str
	time: datetime
	frequency: str = "once"
	completed: bool = False

	def __post_init__(self) -> None:
		"""Validate that frequency is one of the allowed values."""
		allowed_frequencies = {"once", "daily", "weekly", "monthly"}
		if self.frequency not in allowed_frequencies:
			raise ValueError(
				f"frequency must be one of {sorted(allowed_frequencies)}"
			)

	def mark_complete(self) -> None:
		"""Mark the task as completed."""
		self.completed = True

	def mark_incomplete(self) -> None:
		"""Reset the task to incomplete."""
		self.completed = False

	def is_overdue(self, current_time: datetime) -> bool:
		"""Return True if the task is past due and not yet completed."""
		return not self.completed and self.time < current_time

	def occurs_on(self, target_date: date) -> bool:
		"""Return whether this task should appear on the target date."""
		if self.frequency == "once":
			return self.time.date() == target_date
		if self.frequency == "daily":
			return self.time.date() <= target_date
		if self.frequency == "weekly":
			return self.time.date() <= target_date and self.time.weekday() == target_date.weekday()
		# monthly
		return self.time.date() <= target_date and self.time.day == target_date.day


@dataclass
class Pet:
	name: str
	species: str
	age: int
	preferences: dict[str, Any] = field(default_factory=dict)
	tasks: list[Task] = field(default_factory=list)

	def update_profile(
		self,
		name: str | None = None,
		age: int | None = None,
		preferences: dict[str, Any] | None = None,
	) -> None:
		"""Update one or more profile fields; omitted fields are left unchanged."""
		if name is not None:
			self.name = name
		if age is not None:
			self.age = age
		if preferences is not None:
			self.preferences.update(preferences)

	def get_preferences(self) -> dict[str, Any]:
		"""Return a copy of this pet's preferences dictionary."""
		return dict(self.preferences)

	def add_task(self, task: Task) -> None:
		"""Append a task to this pet's task list."""
		self.tasks.append(task)

	def remove_task(self, task: Task) -> None:
		"""Remove a task from this pet's task list."""
		self.tasks.remove(task)

	def get_tasks(self, include_completed: bool = True) -> list[Task]:
		"""Return all tasks for this pet, optionally filtering out completed ones."""
		if include_completed:
			return list(self.tasks)
		return [task for task in self.tasks if not task.completed]


@dataclass
class Owner:
	name: str
	pets: list[Pet] = field(default_factory=list)

	def add_pet(self, pet: Pet) -> None:
		"""Add a pet to this owner's roster, raising an error on duplicate names."""
		if any(existing_pet.name == pet.name for existing_pet in self.pets):
			raise ValueError(f"Pet named '{pet.name}' already exists")
		self.pets.append(pet)

	def remove_pet(self, pet_name: str) -> None:
		"""Remove a pet by name, raising an error if no matching pet is found."""
		pet = self.get_pet(pet_name)
		if pet is None:
			raise ValueError(f"No pet named '{pet_name}' found")
		self.pets.remove(pet)

	def get_pet(self, pet_name: str) -> Pet | None:
		"""Return the pet with the given name, or None if not found."""
		for pet in self.pets:
			if pet.name == pet_name:
				return pet
		return None

	def get_all_tasks(self, include_completed: bool = True) -> list[Task]:
		"""Aggregate and return tasks from all pets owned by this owner."""
		all_tasks: list[Task] = []
		for pet in self.pets:
			all_tasks.extend(pet.get_tasks(include_completed=include_completed))
		return all_tasks


class Scheduler:
	def get_all_tasks(self, owner: Owner, include_completed: bool = False) -> list[Task]:
		"""Return all tasks across the owner's pets via the owner's aggregator."""
		return owner.get_all_tasks(include_completed=include_completed)

	def build_today_plan(self, owner: Owner, current_time: datetime | None = None) -> list[Task]:
		"""Return all incomplete tasks due today, sorted chronologically."""
		now = current_time or datetime.now()
		today = now.date()
		tasks_for_today = [
			task
			for task in owner.get_all_tasks(include_completed=False)
			if task.occurs_on(today)
		]
		return sorted(tasks_for_today, key=lambda task: task.time)

	def get_upcoming_tasks(
		self,
		owner: Owner,
		current_time: datetime | None = None,
		within_hours: int = 24,
	) -> list[Task]:
		"""Return incomplete tasks due within the next N hours, sorted by time."""
		now = current_time or datetime.now()
		end_time = now + timedelta(hours=within_hours)
		candidates = owner.get_all_tasks(include_completed=False)
		upcoming = [task for task in candidates if now <= task.time <= end_time]
		return sorted(upcoming, key=lambda task: task.time)

	def complete_task(self, owner: Owner, task: Task) -> None:
		"""Mark a task as complete after verifying it belongs to the owner."""
		if task not in owner.get_all_tasks(include_completed=True):
			raise ValueError("Task does not belong to this owner")
		task.mark_complete()

	def organize_tasks_by_pet(self, owner: Owner) -> dict[str, list[Task]]:
		"""Return a dict mapping each pet's name to its time-sorted task list."""
		organized: dict[str, list[Task]] = {}
		for pet in owner.pets:
			organized[pet.name] = sorted(
				pet.get_tasks(include_completed=True),
				key=lambda task: task.time,
			)
		return organized
