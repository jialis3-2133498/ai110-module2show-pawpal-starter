# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Features

### Priority + time-of-day sorting

`Tasks.get_tasks_by_priority()` sorts tasks by a two-key algorithm: numeric priority first (1 = highest), then by `due_time` in chronological order (`morning → afternoon → evening → anytime`). Implemented using Python's `sorted()` with a compound lambda key. This prevents a low-priority afternoon task from being scheduled before a same-priority morning task.

### Greedy scheduling

`TasksPlanner.schedule()` zips priority-sorted tasks with available time slots in one pass. Each task is matched to the next open slot sequentially. Tasks that exceed the number of available slots are silently dropped, and the count is surfaced as a warning to the owner.

### Availability-aware scheduling

`Constraint.get_available_slots()` excludes any `TimeSlot` where `available=False` before scheduling begins. Busy windows (commutes, meetings) are never assigned a task regardless of priority.

### Daily and weekly recurrence

`Task` has two optional fields: `recurrence` (`"daily"`, `"weekly"`, or `None`) and `due_date` (defaults to today). When `Tasks.complete_task(task)` is called on a recurring task, it marks the original complete and automatically appends a new instance to the task list with the next due date calculated using Python's `timedelta`:

- `"daily"` → `due_date + 1 day`
- `"weekly"` → `due_date + 7 days`

One-off tasks (no recurrence) return `None` and are simply marked done.

### Two-layer conflict detection

Two layers of conflict detection run before the schedule prints, neither of which crashes the program:

- **`Constraint.get_conflicts()`** — detects overlapping time slot definitions by sorting available slots by start time and checking whether any slot's `end > next.start` (lexicographic `HH:MM` comparison).
- **`TasksPlanner.get_conflicts(plan)`** — detects duplicate slot assignments in the final plan — two tasks paired to the same time slot key. Accepts a pre-built plan to avoid running the scheduling algorithm twice.

Warnings are surfaced with a `⚠` prefix so the owner sees conflicts immediately while still getting a usable plan.

### Flexible task filtering

`Tasks.filter_tasks(pet_name, completed)` queries the task list by any combination of pet name and completion status. Both parameters are optional and AND together, so callers can ask for all pending tasks, all tasks for one pet, or completed tasks for a specific pet in a single call.

## Testing PawPal+

### Running the tests

```bash
python -m pytest tests/test_pawpal.py -v
```

If pytest is not installed, run the test file directly:

```bash
python tests/test_pawpal.py
```

### What the tests cover

| Area | Tests | What is verified |
|---|---|---|
| **Task completion** | `test_mark_complete_changes_status` | `completed` flips from `False` to `True` after `mark_complete()` |
| **Task addition** | `test_feed_pet_increases_task_count` | Adding feed, walk, and groom tasks grows `task_list` to 3 |
| **Sorting — priority** | `test_get_tasks_by_priority_returns_chronological_order` | Tasks added out of order are returned P1 → P2 → P3 |
| **Sorting — tie-breaking** | `test_get_tasks_by_priority_sorts_by_due_time_within_same_priority` | Same-priority tasks sort `morning` before `evening` |
| **Recurrence — daily** | `test_complete_daily_task_creates_next_day_task` | Completing a daily task spawns a new task due the next day with all fields preserved |
| **Recurrence — none** | `test_complete_non_recurring_task_returns_none` | Completing a one-off task returns `None` and does not grow the task list |
| **Conflict detection — overlap** | `test_get_conflicts_flags_overlapping_slots` | Slots `09:00–10:00` and `09:30–10:30` produce exactly one conflict warning |
| **Conflict detection — adjacent** | `test_get_conflicts_does_not_flag_adjacent_slots` | Slots `08:00–09:00` and `09:00–10:00` produce zero conflict warnings (boundary condition) |

### Confidence Level

**★★★★☆ (4/5)**

The core scheduling behaviors — priority sorting, recurring task generation, and conflict detection — are tested against both the happy path and key edge cases (tie-breaking, adjacent boundaries, one-off vs. recurring). The main gap is end-to-end coverage of `TasksPlanner.schedule()` and the Streamlit UI layer, which remain untested. Confidence in the Python logic is high; confidence in the full integrated system is moderate until those layers have coverage.
