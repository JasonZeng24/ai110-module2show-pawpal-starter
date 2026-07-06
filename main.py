"""CLI demo/testing ground for the PawPal+ logic layer."""

from datetime import date

from pawpal_system import Owner, Pet, Task, Scheduler


def print_schedule(title, tasks):
    print(f"\n{title}")
    if not tasks:
        print("  (no tasks)")
        return
    for t in tasks:
        status = "✅" if t.completed else "⬜"
        print(f"  {status} {t.time}  {t.pet_name:<10} {t.description} "
              f"({t.duration_minutes} min, {t.priority} priority, {t.frequency})")


def main():
    owner = Owner("Jordan")
    mochi = owner.add_pet(Pet("Mochi", "dog"))
    biscuit = owner.add_pet(Pet("Biscuit", "cat"))

    today = date.today()

    # Tasks added out of order on purpose, to prove sorting works.
    mochi.add_task(Task("Evening walk", "18:00", frequency="daily", priority="high", date=today))
    mochi.add_task(Task("Morning walk", "08:00", frequency="daily", priority="high", date=today))
    biscuit.add_task(Task("Feeding", "08:00", frequency="daily", priority="high", date=today))
    biscuit.add_task(Task("Litter box check", "12:30", frequency="once", priority="medium", date=today))
    mochi.add_task(Task("Heartworm medication", "09:00", frequency="weekly", priority="high", date=today))

    scheduler = Scheduler(owner)

    print_schedule("Today's Schedule (sorted by time)", scheduler.get_todays_schedule())

    print_schedule("Mochi's tasks only", scheduler.filter_tasks(pet_name="Mochi"))
    print_schedule("Incomplete tasks only", scheduler.filter_tasks(completed=False))

    print("\nCompleting Mochi's morning walk (daily, should auto-recur)...")
    morning_walk = next(t for t in mochi.tasks if t.description == "Morning walk")
    next_task = scheduler.mark_task_complete(morning_walk)
    print(f"  Marked complete. Next occurrence created for {next_task.date} at {next_task.time}.")

    print("\nAdding a conflicting task for Biscuit at 08:00...")
    biscuit.add_task(Task("Grooming", "08:00", frequency="once", priority="low", date=today))
    conflicts = scheduler.detect_conflicts()
    print_schedule("Today's Schedule (after adding conflict)", scheduler.get_todays_schedule())
    print("\nConflict warnings:")
    if conflicts:
        for warning in conflicts:
            print(f"  {warning}")
    else:
        print("  (none)")


if __name__ == "__main__":
    main()
