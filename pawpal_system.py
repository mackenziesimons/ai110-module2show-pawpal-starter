from __future__ import annotations

import calendar
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

	def next_occurrence(self) -> Task | None:
		"""Return a new task for the next recurrence, or None for one-time tasks."""
		if self.frequency == "once":
			return None
		if self.frequency == "daily":
			next_time = self.time + timedelta(days=1)
		elif self.frequency == "weekly":
			next_time = self.time + timedelta(weeks=1)
		else:
			year = self.time.year
			month = self.time.month + 1
			if month == 13:
				month = 1
				year += 1
			day = min(self.time.day, calendar.monthrange(year, month)[1])
			next_time = self.time.replace(year=year, month=month, day=day)

		return Task(
			description=self.description,
			time=next_time,
			frequency=self.frequency,
		)

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

	def sort_by_time(self, tasks: list[Task]) -> list[Task]:
		"""Return a new task list sorted by due time."""
		return sorted(tasks, key=lambda task: task.time)

	def filter_tasks(
		self,
		owner: Owner,
		pet_name: str | None = None,
		completed: bool | None = None,
	) -> list[Task]:
		"""Return tasks filtered by pet name and/or completion status, sorted by time."""
		filtered_tasks: list[Task] = []
		for pet in owner.pets:
			if pet_name is not None and pet.name != pet_name:
				continue
			for task in pet.get_tasks(include_completed=True):
				if completed is not None and task.completed != completed:
					continue
				filtered_tasks.append(task)
		return self.sort_by_time(filtered_tasks)

	def build_today_plan(self, owner: Owner, current_time: datetime | None = None) -> list[Task]:
		"""Return all incomplete tasks due today, sorted chronologically."""
		now = current_time or datetime.now()
		today = now.date()
		tasks_for_today = [
			task
			for task in owner.get_all_tasks(include_completed=False)
			if task.occurs_on(today)
		]
		return self.sort_by_time(tasks_for_today)

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
		return self.sort_by_time(upcoming)

	def complete_task(self, owner: Owner, task: Task) -> Task | None:
		"""Mark a task as complete and create the next recurring task when needed."""
		pet = self.find_pet_for_task(owner, task)
		if pet is None:
			raise ValueError("Task does not belong to this owner")
		if task.completed:
			raise ValueError("Task is already completed")
		task.mark_complete()
		next_task = task.next_occurrence()
		if next_task is not None:
			pet.add_task(next_task)
		return next_task

	def mark_task_complete(self, owner: Owner, task: Task) -> Task | None:
		"""Mark a task complete and create its next occurrence for recurring tasks."""
		return self.complete_task(owner, task)

	def find_pet_for_task(self, owner: Owner, task: Task) -> Pet | None:
		"""Return the pet that owns the given task, or None if it is not found."""
		for pet in owner.pets:
			if task in pet.tasks:
				return pet
		return None

	def detect_conflicts(self, owner: Owner, include_completed: bool = False) -> list[str]:
		"""Return warning messages for tasks that share the exact same scheduled time."""
		warnings: list[str] = []
		tasks_with_pets: list[tuple[Task, Pet]] = []
		for pet in owner.pets:
			for task in pet.get_tasks(include_completed=include_completed):
				tasks_with_pets.append((task, pet))

		sorted_tasks_with_pets = sorted(tasks_with_pets, key=lambda item: item[0].time)
		for index in range(len(sorted_tasks_with_pets) - 1):
			current_task, current_pet = sorted_tasks_with_pets[index]
			next_task, next_pet = sorted_tasks_with_pets[index + 1]
			if current_task.time != next_task.time:
				continue
			warnings.append(
				(
					"Conflict detected at "
					f"{current_task.time.strftime('%Y-%m-%d %H:%M')}: "
					f"{current_pet.name} - {current_task.description} and "
					f"{next_pet.name} - {next_task.description}"
				)
			)
		return warnings

	def organize_tasks_by_pet(self, owner: Owner) -> dict[str, list[Task]]:
		"""Return a dict mapping each pet's name to its time-sorted task list."""
		organized: dict[str, list[Task]] = {}
		for pet in owner.pets:
			organized[pet.name] = self.sort_by_time(pet.get_tasks(include_completed=True))
		return organized
