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

## 🖥️ Sample Output

Output from running `python main.py`:

```
Today's Schedule (sorted by time)
  ⬜ 08:00  Mochi      Morning walk (15 min, high priority, daily)
  ⬜ 08:00  Biscuit    Feeding (15 min, high priority, daily)
  ⬜ 09:00  Mochi      Heartworm medication (15 min, high priority, weekly)
  ⬜ 12:30  Biscuit    Litter box check (15 min, medium priority, once)
  ⬜ 18:00  Mochi      Evening walk (15 min, high priority, daily)

Mochi's tasks only
  ⬜ 18:00  Mochi      Evening walk (15 min, high priority, daily)
  ⬜ 08:00  Mochi      Morning walk (15 min, high priority, daily)
  ⬜ 09:00  Mochi      Heartworm medication (15 min, high priority, weekly)

Incomplete tasks only
  ⬜ 18:00  Mochi      Evening walk (15 min, high priority, daily)
  ⬜ 08:00  Mochi      Morning walk (15 min, high priority, daily)
  ⬜ 09:00  Mochi      Heartworm medication (15 min, high priority, weekly)
  ⬜ 08:00  Biscuit    Feeding (15 min, high priority, daily)
  ⬜ 12:30  Biscuit    Litter box check (15 min, medium priority, once)

Completing Mochi's morning walk (daily, should auto-recur)...
  Marked complete. Next occurrence created for 2026-07-07 at 08:00.

Adding a conflicting task for Biscuit at 08:00...

Today's Schedule (after adding conflict)
  ✅ 08:00  Mochi      Morning walk (15 min, high priority, daily)
  ⬜ 08:00  Biscuit    Feeding (15 min, high priority, daily)
  ⬜ 08:00  Biscuit    Grooming (15 min, low priority, once)
  ⬜ 09:00  Mochi      Heartworm medication (15 min, high priority, weekly)
  ⬜ 12:30  Biscuit    Litter box check (15 min, medium priority, once)
  ⬜ 18:00  Mochi      Evening walk (15 min, high priority, daily)

Conflict warnings:
  ⚠️ Conflict at 08:00 on 2026-07-06: Mochi (Morning walk), Biscuit (Feeding), Biscuit (Grooming)
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Test coverage: `Task.mark_complete()`, task-to-pet association, chronological sorting,
filtering by pet and completion status, daily recurrence (next occurrence created a day
later), one-off tasks not recurring, and conflict detection (both the duplicate-time and
no-conflict cases).

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.9.7, pytest-8.4.2, pluggy-1.6.0
rootdir: PawPal-Plus
collecting ... collected 10 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [ 10%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED      [ 20%]
tests/test_pawpal.py::test_add_task_stamps_pet_name PASSED               [ 30%]
tests/test_pawpal.py::test_sorting_returns_tasks_in_chronological_order PASSED [ 40%]
tests/test_pawpal.py::test_filter_by_pet_name PASSED                     [ 50%]
tests/test_pawpal.py::test_filter_by_completion_status PASSED            [ 60%]
tests/test_pawpal.py::test_recurrence_creates_task_for_next_day PASSED   [ 70%]
tests/test_pawpal.py::test_one_off_task_does_not_recur PASSED            [ 80%]
tests/test_pawpal.py::test_conflict_detection_flags_duplicate_times PASSED [ 90%]
tests/test_pawpal.py::test_no_conflict_when_times_differ PASSED          [100%]

============================== 10 passed in 1.41s ==============================
```

**Confidence Level:** ⭐⭐⭐⭐☆ (4/5) — core logic (sorting, filtering, recurrence, conflict
detection) is well covered. The main gap is duration-aware overlap detection (see
Tradeoffs in `reflection.md`), which isn't tested because it isn't implemented.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts by the `"HH:MM"` `time` string, which sorts correctly lexicographically since it's zero-padded 24-hour time. |
| Filtering | `Scheduler.filter_tasks(pet_name=..., completed=...)` | Filters by pet name and/or completion status; either argument can be omitted. |
| Conflict handling | `Scheduler.detect_conflicts()` | Groups tasks by `(date, time)`; any group with more than one task returns a warning string instead of raising an error. Scoped to same day so a recurring task doesn't falsely conflict with a past instance of itself. |
| Recurring tasks | `Task.next_occurrence()`, `Scheduler.mark_task_complete()` | When a `daily`/`weekly` task is completed, a fresh `Task` is generated for `date + timedelta(days=1 or 7)` and added back to the same pet. |

## 📸 Demo Walkthrough

1. **Add a pet.** Enter a name and species (e.g., "Mochi", dog) in the "Add a Pet" form and submit — the pet appears in the "Current pets" list.
2. **Add tasks.** Pick a pet from the dropdown, describe the task (e.g., "Morning walk"), set a time, duration, priority, and frequency (`once`/`daily`/`weekly`), then submit. Repeat for a second pet with an overlapping time to see conflict detection in action.
3. **View today's schedule.** The "Today's Schedule" table shows every task sorted chronologically, with an optional filter by pet and a toggle to hide completed tasks.
4. **See conflict warnings.** If two tasks share the same date and time, a `st.warning` banner names both tasks; otherwise a `st.success` banner confirms there are no conflicts.
5. **Mark a task complete.** Choose an incomplete task from the dropdown and click "Mark complete." If it recurs daily/weekly, PawPal+ automatically schedules the next occurrence and confirms this in a success message.

**CLI walkthrough:** run `python main.py` to see the same core logic (sorting, filtering, recurrence, conflict detection) demonstrated end-to-end in the terminal — see the Sample Output section above.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
