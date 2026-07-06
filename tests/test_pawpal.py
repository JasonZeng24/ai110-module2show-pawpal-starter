"""Automated tests for the PawPal+ logic layer."""

from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Task, Scheduler


@pytest.fixture
def owner_with_pets():
    owner = Owner("Jordan")
    mochi = owner.add_pet(Pet("Mochi", "dog"))
    biscuit = owner.add_pet(Pet("Biscuit", "cat"))
    return owner, mochi, biscuit


# --- Task behavior -----------------------------------------------------

def test_mark_complete_changes_status():
    task = Task("Walk", "08:00")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert pet.task_count() == 0
    pet.add_task(Task("Walk", "08:00"))
    assert pet.task_count() == 1


def test_add_task_stamps_pet_name():
    pet = Pet("Mochi", "dog")
    task = pet.add_task(Task("Walk", "08:00"))
    assert task.pet_name == "Mochi"


# --- Sorting -------------------------------------------------------------

def test_sorting_returns_tasks_in_chronological_order(owner_with_pets):
    owner, mochi, biscuit = owner_with_pets
    mochi.add_task(Task("Evening walk", "18:00"))
    mochi.add_task(Task("Morning walk", "08:00"))
    biscuit.add_task(Task("Lunch feeding", "12:30"))

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_by_time()

    times = [t.time for t in sorted_tasks]
    assert times == sorted(times)
    assert times[0] == "08:00"
    assert times[-1] == "18:00"


# --- Filtering -------------------------------------------------------------

def test_filter_by_pet_name(owner_with_pets):
    owner, mochi, biscuit = owner_with_pets
    mochi.add_task(Task("Walk", "08:00"))
    biscuit.add_task(Task("Feeding", "08:00"))

    scheduler = Scheduler(owner)
    mochi_tasks = scheduler.filter_tasks(pet_name="Mochi")

    assert len(mochi_tasks) == 1
    assert mochi_tasks[0].pet_name == "Mochi"


def test_filter_by_completion_status(owner_with_pets):
    owner, mochi, _ = owner_with_pets
    done = mochi.add_task(Task("Walk", "08:00"))
    done.mark_complete()
    mochi.add_task(Task("Feeding", "09:00"))

    scheduler = Scheduler(owner)
    incomplete = scheduler.filter_tasks(completed=False)

    assert len(incomplete) == 1
    assert incomplete[0].description == "Feeding"


# --- Recurrence -------------------------------------------------------------

def test_recurrence_creates_task_for_next_day(owner_with_pets):
    owner, mochi, _ = owner_with_pets
    today = date.today()
    daily_task = mochi.add_task(Task("Morning walk", "08:00", frequency="daily", date=today))

    scheduler = Scheduler(owner)
    next_task = scheduler.mark_task_complete(daily_task)

    assert daily_task.completed is True
    assert next_task is not None
    assert next_task.date == today + timedelta(days=1)
    assert next_task.completed is False
    assert mochi.task_count() == 2


def test_one_off_task_does_not_recur(owner_with_pets):
    owner, mochi, _ = owner_with_pets
    one_off = mochi.add_task(Task("Vet appointment", "10:00", frequency="once"))

    scheduler = Scheduler(owner)
    next_task = scheduler.mark_task_complete(one_off)

    assert next_task is None
    assert mochi.task_count() == 1


# --- Conflict detection -----------------------------------------------------

def test_conflict_detection_flags_duplicate_times(owner_with_pets):
    owner, mochi, biscuit = owner_with_pets
    mochi.add_task(Task("Walk", "08:00"))
    biscuit.add_task(Task("Feeding", "08:00"))

    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1
    assert "08:00" in conflicts[0]


def test_no_conflict_when_times_differ(owner_with_pets):
    owner, mochi, biscuit = owner_with_pets
    mochi.add_task(Task("Walk", "08:00"))
    biscuit.add_task(Task("Feeding", "09:00"))

    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts()

    assert conflicts == []
