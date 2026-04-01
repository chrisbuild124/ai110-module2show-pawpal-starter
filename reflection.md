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

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
