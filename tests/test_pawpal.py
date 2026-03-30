import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date, timedelta
from pawpal_system import Pet, Task, Tasks, Constraint, TimeSlot


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


# --- Test 3: Sorting Correctness ---
def test_get_tasks_by_priority_returns_chronological_order():
    pet = Pet(name="Buddy", breed="Labrador", age=3)
    tracker = Tasks(num_pets=1, pets=[pet])

    # Add tasks out of order: groom (P3/afternoon), walk (P2/anytime), feed (P1/morning)
    tracker.groom_pet(pet)   # priority=3, due_time="afternoon"
    tracker.walk_pet(pet)    # priority=2, due_time="anytime"
    tracker.feed_pet(pet)    # priority=1, due_time="morning"

    sorted_tasks = tracker.get_tasks_by_priority()

    assert sorted_tasks[0].task_type == "feed", "Highest priority (P1) task should come first."
    assert sorted_tasks[1].task_type == "walk", "Medium priority (P2) task should come second."
    assert sorted_tasks[2].task_type == "groom", "Lowest priority (P3) task should come last."


def test_get_tasks_by_priority_sorts_by_due_time_within_same_priority():
    pet = Pet(name="Whiskers", breed="Persian Cat", age=5)
    tracker = Tasks(num_pets=1, pets=[pet])

    # Manually add two tasks with the same priority but different due_times
    evening_task = Task(task_type="walk", pet=pet, priority=2, due_time="evening")
    morning_task = Task(task_type="groom", pet=pet, priority=2, due_time="morning")
    tracker.task_list.extend([evening_task, morning_task])

    sorted_tasks = tracker.get_tasks_by_priority()

    assert sorted_tasks[0].due_time == "morning", "morning should sort before evening at the same priority."
    assert sorted_tasks[1].due_time == "evening", "evening should sort after morning at the same priority."


# --- Test 4: Recurrence Logic ---
def test_complete_daily_task_creates_next_day_task():
    pet = Pet(name="Rex", breed="Beagle", age=1)
    tracker = Tasks(num_pets=1, pets=[pet])

    today = date(2026, 3, 30)
    task = Task(task_type="feed", pet=pet, priority=1, due_time="morning",
                recurrence="daily", due_date=today)
    tracker.task_list.append(task)

    next_task = tracker.complete_task(task)

    assert next_task is not None, "complete_task should return a new Task for a daily recurring task."
    assert next_task.due_date == today + timedelta(days=1), "Next task should be due the following day."
    assert next_task.task_type == task.task_type, "Spawned task should preserve task_type."
    assert next_task.recurrence == "daily", "Spawned task should preserve recurrence."
    assert len(tracker.task_list) == 2, "Task list should contain the original and the new recurring task."


def test_complete_non_recurring_task_returns_none():
    pet = Pet(name="Mochi", breed="Shiba Inu", age=4)
    tracker = Tasks(num_pets=1, pets=[pet])

    task = tracker.feed_pet(pet)  # recurrence defaults to None

    result = tracker.complete_task(task)

    assert result is None, "complete_task should return None for a non-recurring task."
    assert len(tracker.task_list) == 1, "No new task should be added for a non-recurring task."


# --- Test 5: Conflict Detection ---
def test_get_slot_overlaps_flags_overlapping_slots():
    overlapping_slots = [
        TimeSlot(start="09:00", end="10:00", available=True),
        TimeSlot(start="09:30", end="10:30", available=True),  # overlaps with above
    ]
    constraint = Constraint(owner_name="Alex", time_slots=overlapping_slots)

    conflicts = constraint.get_slot_overlaps()

    assert len(conflicts) == 1, "One conflict should be detected for overlapping slots."
    assert "09:00" in conflicts[0] and "09:30" in conflicts[0], \
        "Conflict message should reference both overlapping slot start times."


def test_get_slot_overlaps_does_not_flag_adjacent_slots():
    adjacent_slots = [
        TimeSlot(start="08:00", end="09:00", available=True),
        TimeSlot(start="09:00", end="10:00", available=True),  # starts exactly when previous ends
    ]
    constraint = Constraint(owner_name="Alex", time_slots=adjacent_slots)

    conflicts = constraint.get_slot_overlaps()

    assert len(conflicts) == 0, "Adjacent (non-overlapping) slots should not be flagged as conflicts."


if __name__ == "__main__":
    test_mark_complete_changes_status()
    print("PASSED: test_mark_complete_changes_status")

    test_feed_pet_increases_task_count()
    print("PASSED: test_feed_pet_increases_task_count")

    test_get_tasks_by_priority_returns_chronological_order()
    print("PASSED: test_get_tasks_by_priority_returns_chronological_order")

    test_get_tasks_by_priority_sorts_by_due_time_within_same_priority()
    print("PASSED: test_get_tasks_by_priority_sorts_by_due_time_within_same_priority")

    test_complete_daily_task_creates_next_day_task()
    print("PASSED: test_complete_daily_task_creates_next_day_task")

    test_complete_non_recurring_task_returns_none()
    print("PASSED: test_complete_non_recurring_task_returns_none")

    test_get_slot_overlaps_flags_overlapping_slots()
    print("PASSED: test_get_slot_overlaps_flags_overlapping_slots")

    test_get_slot_overlaps_does_not_flag_adjacent_slots()
    print("PASSED: test_get_slot_overlaps_does_not_flag_adjacent_slots")
