# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- The initial UML used four classes: Owner, Pet, Task, and Scheduler.
- Owner was responsible for storing multiple pets and exposing all pet tasks.
- Pet held basic pet metadata and a list of tasks.
- Task represented a single scheduled item with a description, time, frequency, and completion status.
- Scheduler handled cross-pet scheduling logic, including sorting, filtering, and schedule generation.

**b. Design changes**

- Yes, the design evolved during implementation.
- I added `due_date` and `priority` to Task so the app could support recurrence and richer sorting.
- I also added a `to_dict()` helper to simplify Streamlit table rendering and keep UI code cleaner.
- Scheduler gained a dedicated `mark_task_complete()` flow that creates the next recurring task for daily/weekly items.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- The scheduler considers due date, HH:MM time, task completion state, pet name filters, and priority.
- I prioritized date/time ordering first because users usually think in calendar order.
- I treated priority as a secondary ordering factor and recurrence as a completion-time behavior rather than a ranking rule.

**b. Tradeoffs**

- The conflict detector checks only exact date/time collisions and does not model overlapping durations.
- This tradeoff keeps the implementation lightweight and easy to reason about while still surfacing the most obvious scheduling mistakes.
- For this project scope, exact-match collision warnings provide useful value without overcomplicating the data model.

---

## 3. AI Collaboration

**a. How you used AI**

- I used AI to accelerate class scaffolding, refine scheduler method structure, and draft test cases.
- AI was also helpful for quickly validating implementation sequencing: logic layer first, then CLI demo, then Streamlit wiring.
- The most helpful prompts were specific and code-scoped, for example asking how Scheduler should retrieve all tasks from Owner/Pet relationships.

**b. Judgment and verification**

- I rejected a more complex conflict strategy that required task durations and overlap windows.
- I kept exact-time conflict detection because it matched project requirements better and avoided unnecessary complexity.
- I verified decisions by running a CLI demo and automated tests to confirm behavior remained correct.

---

## 4. Testing and Verification

**a. What you tested**

- I tested task completion state updates, pet task addition, time sorting order, daily recurrence generation, and conflict detection.
- These tests covered both baseline object behavior and scheduler intelligence features.
- They were important because they validate core interactions between classes and prevent regressions in algorithmic logic.

**b. Confidence**

- I am reasonably confident (4/5) that the scheduler works for the project scope.
- Next edge cases to test would include invalid time formats, duplicate pets with similar names, large task lists, and weekly recurrence around month/year boundaries.

---

## 5. Reflection

**a. What went well**

- The strongest outcome was the clear separation between backend logic and UI. The CLI-first workflow made debugging simpler before Streamlit integration.

**b. What you would improve**

- I would add JSON persistence and richer conflict handling based on task duration.
- I would also add editing/deleting tasks from the UI to support a full lifecycle.

**c. Key takeaway**

- The key lesson was that AI is most effective when the human defines architecture boundaries first.
- Acting as the lead architect means accepting AI speed benefits while still verifying each design choice against requirements and readability.
