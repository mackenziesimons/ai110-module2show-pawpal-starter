from __future__ import annotations

from datetime import datetime

from pawpal_system import Owner, Pet, Scheduler, Task


def build_sample_data() -> Owner:
	owner = Owner(name="Jordan")

	dog = Pet(name="Mochi", species="dog", age=3)
	cat = Pet(name="Luna", species="cat", age=5)

	owner.add_pet(dog)
	owner.add_pet(cat)

	now = datetime.now()

	dog.add_task(
		Task(
			description="Feed breakfast",
			time=now.replace(hour=9, minute=0, second=0, microsecond=0),
			frequency="daily",
		)
	)
	cat.add_task(
		Task(
			description="Brush coat",
			time=now.replace(hour=7, minute=30, second=0, microsecond=0),
			frequency="once",
			completed=True,
		)
	)
	dog.add_task(
		Task(
			description="Morning walk",
			time=now.replace(hour=8, minute=0, second=0, microsecond=0),
			frequency="daily",
		)
	)
	dog.add_task(
		Task(
			description="Medication",
			time=now.replace(hour=8, minute=0, second=0, microsecond=0),
			frequency="once",
		)
	)
	cat.add_task(
		Task(
			description="Play session",
			time=now.replace(hour=18, minute=30, second=0, microsecond=0),
			frequency="daily",
		)
	)
	cat.add_task(
		Task(
			description="Litter cleanup",
			time=now.replace(hour=18, minute=30, second=0, microsecond=0),
			frequency="weekly",
		)
	)

	return owner


def print_task_list(title: str, tasks: list[Task], owner: Owner, scheduler: Scheduler) -> None:
	print(title)
	print("=" * len(title))

	if not tasks:
		print("No tasks found.")
		return

	for task in tasks:
		pet = scheduler.find_pet_for_task(owner, task)
		pet_name = pet.name if pet is not None else "Unknown"
		status = "done" if task.completed else "pending"
		print(f"- {task.time.strftime('%I:%M %p')} | {pet_name} | {task.description} [{status}]")


def print_todays_schedule(owner: Owner, scheduler: Scheduler) -> None:
	today_tasks = scheduler.build_today_plan(owner, current_time=datetime.now())
	organized = scheduler.organize_tasks_by_pet(owner)

	print("Today's Schedule")
	print("=" * 16)

	if not today_tasks:
		print("No tasks scheduled for today.")
		return

	for pet in owner.pets:
		pet_tasks = [task for task in organized[pet.name] if task.occurs_on(datetime.now().date())]
		if not pet_tasks:
			continue

		print(f"\n{pet.name} ({pet.species})")
		for task in pet_tasks:
			status = "done" if task.completed else "pending"
			print(f"- {task.time.strftime('%I:%M %p')}: {task.description} [{status}]")


def print_conflicts(owner: Owner, scheduler: Scheduler) -> None:
	warnings = scheduler.detect_conflicts(owner)
	print("\nConflict Warnings")
	print("=" * 17)
	if not warnings:
		print("No conflicts detected.")
		return
	for warning in warnings:
		print(f"- {warning}")


def demonstrate_recurring_completion(owner: Owner, scheduler: Scheduler) -> None:
	morning_walk = scheduler.filter_tasks(owner, pet_name="Mochi", completed=False)[0]
	next_task = scheduler.complete_task(owner, morning_walk)

	print("\nRecurring Task Demo")
	print("=" * 19)
	print(f"Completed: {morning_walk.description} at {morning_walk.time.strftime('%Y-%m-%d %H:%M')}")
	if next_task is not None:
		print(
			"Created next occurrence: "
			f"{next_task.description} at {next_task.time.strftime('%Y-%m-%d %H:%M')}"
		)


if __name__ == "__main__":
	owner_data = build_sample_data()
	scheduler = Scheduler()
	print_task_list(
		"All Tasks Sorted by Time",
		scheduler.sort_by_time(owner_data.get_all_tasks(include_completed=True)),
		owner_data,
		scheduler,
	)
	print()
	print_task_list(
		"Mochi Tasks",
		scheduler.filter_tasks(owner_data, pet_name="Mochi"),
		owner_data,
		scheduler,
	)
	print()
	print_task_list(
		"Completed Tasks",
		scheduler.filter_tasks(owner_data, completed=True),
		owner_data,
		scheduler,
	)
	print()
	print_task_list(
		"Mochi Pending Tasks",
		scheduler.filter_tasks(owner_data, pet_name="Mochi", completed=False),
		owner_data,
		scheduler,
	)
	print()
	print_todays_schedule(owner_data, scheduler)
	print_conflicts(owner_data, scheduler)
	demonstrate_recurring_completion(owner_data, scheduler)
