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
			description="Morning walk",
			time=now.replace(hour=8, minute=0, second=0, microsecond=0),
			frequency="daily",
		)
	)
	dog.add_task(
		Task(
			description="Feed breakfast",
			time=now.replace(hour=9, minute=0, second=0, microsecond=0),
			frequency="daily",
		)
	)
	cat.add_task(
		Task(
			description="Play session",
			time=now.replace(hour=18, minute=30, second=0, microsecond=0),
			frequency="daily",
		)
	)

	return owner


def print_todays_schedule(owner: Owner) -> None:
	scheduler = Scheduler()
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


if __name__ == "__main__":
	owner_data = build_sample_data()
	print_todays_schedule(owner_data)
