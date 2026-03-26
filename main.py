from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def print_schedule(tasks: list[Task], heading: str) -> None:
    """Prints a readable schedule table for CLI demos."""
    print(f"\n{heading}")
    print("-" * len(heading))
    if not tasks:
        print("No tasks found.")
        return

    print(f"{'Date':<12} {'Time':<6} {'Pet':<10} {'Priority':<8} {'Status':<10} Description")
    for task in tasks:
        status = "Done" if task.completed else "Pending"
        print(
            f"{task.due_date.isoformat():<12} {task.time:<6} {task.pet_name or 'N/A':<10} "
            f"{task.priority:<8} {status:<10} {task.description}"
        )


def build_demo_data() -> Scheduler:
    """Builds sample owner, pets, and tasks for a realistic demo run."""
    owner = Owner("Jordan")
    mochi = Pet(name="Mochi", species="dog", age=4)
    luna = Pet(name="Luna", species="cat", age=2)

    owner.add_pet(mochi)
    owner.add_pet(luna)

    owner.add_task_to_pet(
        "Mochi",
        Task(description="Evening walk", time="18:00", frequency="daily", priority="high"),
    )
    owner.add_task_to_pet(
        "Mochi",
        Task(description="Breakfast", time="08:00", frequency="daily", priority="high"),
    )
    owner.add_task_to_pet(
        "Luna",
        Task(description="Medication", time="08:00", frequency="once", priority="high"),
    )
    owner.add_task_to_pet(
        "Luna",
        Task(description="Play session", time="15:30", frequency="weekly", priority="medium"),
    )

    return Scheduler(owner)


def main() -> None:
    """Runs the CLI-first validation flow for PawPal+ logic."""
    scheduler = build_demo_data()

    todays_tasks = scheduler.todays_schedule()
    print_schedule(todays_tasks, "Today's Schedule")

    warnings = scheduler.detect_conflicts(todays_tasks)
    if warnings:
        print("\nConflicts")
        print("---------")
        for warning in warnings:
            print(f"- {warning}")

    print("\nCompleting one recurring task (Mochi breakfast at 08:00)...")
    next_task = scheduler.mark_task_complete(
        pet_name="Mochi",
        description="Breakfast",
        time="08:00",
        on_date=date.today(),
    )
    if next_task:
        print(
            f"Recurring task created for {next_task.due_date.isoformat()} "
            f"at {next_task.time} ({next_task.description})"
        )

    updated_tasks = scheduler.filter_tasks(pet_name="Mochi")
    print_schedule(updated_tasks, "Mochi Tasks (After Completion)")


if __name__ == "__main__":
    main()
