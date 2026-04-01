# PawPal+ Project Reflection

## 1. System Design
1. Keep a journal of all the tasks for the pet. 
2. Rank each task by priority, time amount, etc.
3. Provide plans to the user for the user to do. 

**a. Initial design**

I used four classes: `Owner`, `Pet`, `Task`, and `Scheduler`. `Owner` tracks who the user is and how much time they have. `Pet` holds the animal's info and its list of tasks. `Task` stores what needs to be done, how long it takes, and its priority. `Scheduler` is the logic layer — it takes the owner's tasks and time budget and builds a daily plan.

**b. Design changes**

Yes. After reviewing the skeleton I realized `Task` had no way to know which pet it belonged to. Once the scheduler flattens all tasks into one list, that context is lost. I added a `pet_name` field to `Task` so `Pet.add_task()` can stamp the pet's name on each task — that way the scheduler can still say "Mochi's morning walk" when it explains the plan.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers time budget, task priority, and duration. It sorts high-to-low priority with duration as a tiebreaker so shorter equal-priority tasks go first. Time and priority felt like the constraints that matter most to a real owner — you can't do a 30-minute walk if you only have 20 minutes, and medication should always beat optional activities.

**b. Tradeoffs**

The scheduler is greedy — it picks tasks in order and never goes back to reconsider. A long high-priority task can eat the budget and knock out several short lower-priority tasks that would have fit together. I kept it this way because the output is easy to explain: the owner can always see exactly why something got skipped.

---

## 3. AI Collaboration

**a. Most effective Copilot features**

Agent Mode was the most useful — I could describe what I wanted at a high level and it would implement it across the right files without me having to do it piece by piece. Inline Chat was good for smaller questions like how `timedelta` works or why a sort lambda behaves a certain way. Prompts that referenced the actual file (like `#file:pawpal_system.py`) got way better results than vague ones.

**b. An AI suggestion I rejected**

When I asked Copilot to simplify `detect_conflicts()`, it suggested collapsing the nested loop into a one-liner list comprehension. It worked, but the overlap condition became unreadable — you couldn't tell what it was checking without staring at it. I kept the version with named variables (`a_start`, `a_end`, etc.) because that logic is easy to get wrong and clarity matters more than being clever.

**c. How separate chat sessions helped**

Keeping design, implementation, and testing in separate sessions stopped earlier context from bleeding into later decisions. When I was writing tests I wasn't second-guessing the class structure, and when I was building the UI I wasn't thinking about scheduling logic. It made each phase feel focused.

**d. What I learned as the "lead architect"**

AI is fast but it doesn't know what you actually want — it just tries to match the prompt. The times things went sideways were when I gave vague instructions and accepted the output without reading it. The times things went well were when I reviewed what it produced, asked why, and pushed back when something felt off. The design decisions still had to come from me.

---

## 4. Testing and Verification

**a. What you tested**

I tested task completion, pet task counts, sort order, recurrence logic, and conflict detection. The recurrence and conflict tests mattered most — those are the features most likely to break quietly without a clear error message.

**b. Confidence**

Pretty confident in the backend logic — 10/10 tests pass and the edge cases (adjacent tasks, tasks with no time, `"once"` frequency) are all covered. Less confident in the UI side since there are no automated tests for the Streamlit layer. Things like empty form submissions or duplicate pet names could still cause weird behavior.

---

## 5. Reflection

**a. What went well**

The class structure held up well through the whole build. Starting with a clear UML meant I rarely had to go back and rethink how the pieces connected — I just had to fill in the logic.

**b. What you would improve**

I'd add a `required` flag to `Task` so things like medication can never get bumped from the schedule regardless of time constraints. The current greedy approach can technically skip a high-priority task if something else fills the budget first.

**c. Key takeaway**

AI is a good builder but a bad designer. It can implement almost anything you describe, but it won't tell you when your design is wrong — that part is still on you.
