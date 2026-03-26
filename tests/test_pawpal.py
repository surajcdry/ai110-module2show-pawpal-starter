from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_status() -> None:
    task = Task(description="Feed", time="09:00")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count() -> None:
    pet = Pet(name="Mochi", species="dog")
    assert pet.task_count() == 0

    pet.add_task(Task(description="Walk", time="07:30"))

    assert pet.task_count() == 1


def test_sorting_returns_tasks_in_time_order() -> None:
    owner = Owner("Jordan")
    pet = Pet(name="Mochi", species="dog")
    owner.add_pet(pet)

    owner.add_task_to_pet("Mochi", Task(description="Evening walk", time="18:00"))
    owner.add_task_to_pet("Mochi", Task(description="Breakfast", time="08:00"))
    owner.add_task_to_pet("Mochi", Task(description="Midday potty", time="12:00"))

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_by_time()

    assert [task.time for task in sorted_tasks] == ["08:00", "12:00", "18:00"]


def test_daily_recurrence_creates_next_day_task() -> None:
    owner = Owner("Jordan")
    pet = Pet(name="Mochi", species="dog")
    owner.add_pet(pet)

    today = date.today()
    owner.add_task_to_pet(
        "Mochi",
        Task(description="Breakfast", time="08:00", frequency="daily", due_date=today),
    )

    scheduler = Scheduler(owner)
    next_task = scheduler.mark_task_complete(
        pet_name="Mochi", description="Breakfast", time="08:00", on_date=today
    )

    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.completed is False
    assert pet.task_count() == 2


def test_conflict_detection_flags_duplicate_times() -> None:
    owner = Owner("Jordan")
    mochi = Pet(name="Mochi", species="dog")
    luna = Pet(name="Luna", species="cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)

    owner.add_task_to_pet("Mochi", Task(description="Walk", time="08:00"))
    owner.add_task_to_pet("Luna", Task(description="Medication", time="08:00"))

    scheduler = Scheduler(owner)
    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "Conflict" in warnings[0]
    assert "08:00" in warnings[0]
