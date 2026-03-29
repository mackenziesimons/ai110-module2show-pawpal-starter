from datetime import datetime

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_status():
    task = Task(description="Feed breakfast", time=datetime(2026, 3, 29, 9, 0))
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog", age=3)
    assert len(pet.tasks) == 0
    pet.add_task(Task(description="Morning walk", time=datetime(2026, 3, 29, 8, 0)))
    assert len(pet.tasks) == 1


def test_sort_by_time_orders_tasks_chronologically():
    scheduler = Scheduler()
    tasks = [
        Task(description="Breakfast", time=datetime(2026, 3, 29, 9, 0)),
        Task(description="Walk", time=datetime(2026, 3, 29, 8, 0)),
    ]

    sorted_tasks = scheduler.sort_by_time(tasks)

    assert [task.description for task in sorted_tasks] == ["Walk", "Breakfast"]


def test_filter_tasks_by_pet_and_status_returns_matching_tasks():
    owner = Owner(name="Jordan")
    dog = Pet(name="Mochi", species="dog", age=3)
    cat = Pet(name="Luna", species="cat", age=5)
    owner.add_pet(dog)
    owner.add_pet(cat)

    completed_task = Task(description="Breakfast", time=datetime(2026, 3, 29, 9, 0), completed=True)
    pending_task = Task(description="Walk", time=datetime(2026, 3, 29, 8, 0))
    dog.add_task(completed_task)
    dog.add_task(pending_task)
    cat.add_task(Task(description="Play", time=datetime(2026, 3, 29, 10, 0)))

    filtered_tasks = Scheduler().filter_tasks(owner, pet_name="Mochi", completed=False)

    assert [task.description for task in filtered_tasks] == ["Walk"]


def test_filter_tasks_by_completion_status_returns_all_completed_tasks():
    owner = Owner(name="Jordan")
    dog = Pet(name="Mochi", species="dog", age=3)
    cat = Pet(name="Luna", species="cat", age=5)
    owner.add_pet(dog)
    owner.add_pet(cat)

    dog.add_task(Task(description="Breakfast", time=datetime(2026, 3, 29, 9, 0), completed=True))
    cat.add_task(Task(description="Brush coat", time=datetime(2026, 3, 29, 7, 30), completed=True))
    cat.add_task(Task(description="Play", time=datetime(2026, 3, 29, 10, 0)))

    filtered_tasks = Scheduler().filter_tasks(owner, completed=True)

    assert [task.description for task in filtered_tasks] == ["Brush coat", "Breakfast"]


def test_complete_recurring_task_creates_next_occurrence():
    owner = Owner(name="Jordan")
    dog = Pet(name="Mochi", species="dog", age=3)
    owner.add_pet(dog)
    task = Task(
        description="Morning walk",
        time=datetime(2026, 3, 29, 8, 0),
        frequency="daily",
    )
    dog.add_task(task)

    next_task = Scheduler().complete_task(owner, task)

    assert task.completed is True
    assert next_task is not None
    assert next_task.time == datetime(2026, 3, 30, 8, 0)
    assert next_task.completed is False
    assert len(dog.tasks) == 2


def test_mark_task_complete_creates_next_weekly_occurrence():
    owner = Owner(name="Jordan")
    dog = Pet(name="Mochi", species="dog", age=3)
    owner.add_pet(dog)
    task = Task(
        description="Weekly grooming",
        time=datetime(2026, 3, 29, 15, 0),
        frequency="weekly",
    )
    dog.add_task(task)

    next_task = Scheduler().mark_task_complete(owner, task)

    assert task.completed is True
    assert next_task is not None
    assert next_task.time == datetime(2026, 4, 5, 15, 0)
    assert next_task.frequency == "weekly"
    assert next_task.completed is False
    assert len(dog.tasks) == 2


def test_detect_conflicts_returns_warning_for_same_time_tasks():
    owner = Owner(name="Jordan")
    dog = Pet(name="Mochi", species="dog", age=3)
    cat = Pet(name="Luna", species="cat", age=5)
    owner.add_pet(dog)
    owner.add_pet(cat)

    dog.add_task(Task(description="Walk", time=datetime(2026, 3, 29, 8, 0)))
    cat.add_task(Task(description="Breakfast", time=datetime(2026, 3, 29, 8, 0)))

    warnings = Scheduler().detect_conflicts(owner)

    assert len(warnings) == 1
    assert "Conflict detected" in warnings[0]
