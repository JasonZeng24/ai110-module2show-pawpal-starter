# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

I identified four core classes based on the scenario: `Task`, `Pet`, `Owner`, and `Scheduler`.

- `Task` represents a single care activity — description, time (`"HH:MM"`), frequency
  (`once`/`daily`/`weekly`), duration, priority, completion status, a `date`, and the name
  of the pet it belongs to. It's a `dataclass` since it's mostly a data container with two
  small behaviors: `mark_complete()` and `next_occurrence()`.
- `Pet` holds a name, species, and its own list of `Task`s. It owns `add_task()` and
  `task_count()`.
- `Owner` manages a list of `Pet`s and exposes `get_all_tasks()` so callers don't need to
  know how tasks are nested inside pets.
- `Scheduler` is the only class with "intelligence" — it takes an `Owner` and provides
  `sort_by_time()`, `filter_tasks()`, `get_todays_schedule()`, `detect_conflicts()`, and
  `mark_task_complete()`. Keeping this logic out of `Owner`/`Pet` kept those two classes
  as simple data holders.

**b. Design changes**

Two changes from the initial sketch:

1. Originally `Task` only had a `time` string, but recurring tasks need to track *which*
   day they're due, not just the time of day. I added a `date` field (defaulting to
   `date.today()`) so daily/weekly recurrence can compute `next_occurrence()` with
   `timedelta` instead of overloading the `time` string to mean two different things.
2. Conflict detection first only compared `time` strings across all tasks, which meant a
   daily task and a completed one-off task from last week would falsely "conflict" if they
   shared a time. Adding `date` to the grouping key in `detect_conflicts()` fixed this —
   conflicts are now scoped to same day *and* same time.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three things: the task's `time` (for ordering), its `date`
(for scoping recurrence and conflicts to a single day), and `priority`/`completed`
status (for filtering). I deliberately left out duration-based packing (e.g., rejecting
a task if it would overflow the owner's available hours) — the scenario is about
*visibility and organization* for a busy owner, not a hard capacity planner, so
surfacing every task with a priority label felt more useful than silently dropping
low-priority ones.

**b. Tradeoffs**

`detect_conflicts()` only flags tasks that share the *exact same* `"HH:MM"` time —
it does not check whether task durations overlap (e.g., a 30-minute walk starting at
08:00 and a 08:15 feeding would not be flagged, even though they overlap in practice).
I chose this because exact-time matching is simple to reason about and cheap to compute
(`O(n)` grouping by key), and it still catches the most common real-world mistake —
double-booking the same time slot. A duration-aware overlap check would need interval
comparison (`O(n log n)` after sorting) for a marginal gain in this scenario's scope.

---

## 3. AI Collaboration

**a. How you used AI**

I used my AI coding assistant across the whole pipeline: brainstorming the four-class
UML from the scenario description, generating the Mermaid diagram source, scaffolding
the dataclasses, writing the CLI demo (`main.py`), drafting the pytest suite, and wiring
`app.py` to `st.session_state`. The most useful prompts were narrow and gave the AI a
specific file plus a specific question — e.g., "based on my `Task`/`Pet`/`Owner` classes,
how should `Scheduler` retrieve all tasks without `Owner` and `Pet` knowing about
`Scheduler`?" — rather than open-ended "build me a scheduler" requests. Narrow prompts
produced code that matched the existing design instead of a different architecture.

**b. Judgment and verification**

One suggestion I modified: an early version of conflict detection compared every pair
of tasks with a nested loop (`O(n²)`), independent of date. I kept the "compare all
pairs" idea for correctness but restructured it to group tasks into a dict keyed by
`(date, time)` first (`O(n)`), then only flag groups with more than one task — same
result, cheaper, and it naturally added the missing date-scoping. I verified the change
by re-running `tests/test_pawpal.py` and the `main.py` demo before and after to confirm
identical conflict output for the existing test cases.

---

## 4. Testing and Verification

**a. What you tested**

Ten tests cover: marking a task complete, adding a task increasing a pet's task count,
a task being stamped with its pet's name, chronological sorting, filtering by pet name,
filtering by completion status, daily recurrence creating a next-day task, one-off tasks
*not* recurring, conflict detection flagging duplicate times, and confirming no false
positives when times differ. These were chosen because they're exactly the behaviors the
scheduler promises in the README's "Smarter Scheduling" table — if any of them silently
broke, the app would show a wrong schedule without crashing.

**b. Confidence**

⭐⭐⭐⭐☆ (4/5). All 10 tests pass and the CLI demo output matches expectations. The
scheduling and recurrence logic is solid; the confidence isn't a full 5 because
conflict detection is time-exact rather than duration-aware overlap detection (see
2b), and there's no test yet for a pet with zero tasks. With more time I'd add: a
zero-task pet edge case, a task added with a malformed `"HH:MM"` string, and a weekly
recurrence test to complement the existing daily one.

---

## 5. Reflection

**a. What went well**

The separation between `Scheduler` (behavior) and `Owner`/`Pet` (data) held up well
through the whole build — I never had to reach into `Scheduler` from `Pet` or vice versa,
which made it easy to add new features (recurrence, conflict detection) as new
`Scheduler` methods without touching the data classes at all.

**b. What you would improve**

I'd upgrade conflict detection to be duration-aware (interval overlap, not just exact
time match) and add a lightweight "explain the plan" method that returns why a task was
ordered where it is (priority vs. time), since the scenario explicitly asks the assistant
to explain its choices, not just list them.

**c. Key takeaway**

Being the "lead architect" with AI meant I spent most of my effort on *design decisions*
(what should `date` mean on a `Task`, where should conflict-checking live) rather than
on typing out boilerplate — but every design decision still needed me to trace through
a concrete example (two tasks, one pet, one time slot) before accepting AI-generated
code, because the AI would readily produce plausible-looking logic that quietly missed
a case like the date-scoping described in 1b.
