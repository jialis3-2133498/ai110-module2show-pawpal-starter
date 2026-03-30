import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Pet, Task, Tasks


# --- Test 1: Task Completion ---
def test_mark_complete_changes_status():
    pet = Pet(name="Luna", breed="Golden Retriever", age=2)
    task = Task(task_type="walk", pet=pet, priority=2, due_time="evening")

    assert task.completed is False, "Task should start as not completed."

    task.mark_complete()

    assert task.completed is True, "Task should be completed after mark_complete()."


# --- Test 2: Task Addition ---
def test_feed_pet_increases_task_count():
    pet = Pet(name="Mochi", breed="Shiba Inu", age=4)
    tracker = Tasks(num_pets=1, pets=[pet])

    assert len(tracker.task_list) == 0, "Task list should start empty."

    tracker.feed_pet(pet)
    tracker.walk_pet(pet)
    tracker.groom_pet(pet)

    assert len(tracker.task_list) == 3, "Task list should have 3 tasks after adding three tasks."


if __name__ == "__main__":
    test_mark_complete_changes_status()
    print("PASSED: test_mark_complete_changes_status")

    test_feed_pet_increases_task_count()
    print("PASSED: test_feed_pet_increases_task_count")
