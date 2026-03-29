from datetime import datetime

from pawpal_system import Pet, Task


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
