# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

**c. Core user actions**

In PawPal+, a user should be able to create and manage pet profiles so each pet has its own details, routines, and care preferences in one place. A user should also be able to schedule and track daily care activities such as walks, feedings, medication, and appointments so nothing important is missed. Finally, a user should be able to open a simple "Today" view that shows upcoming and completed tasks, making it easy to understand what needs attention right now.

**d. Mermaid class diagram**

```mermaid
classDiagram
	class Pet {
		+int pet_id
		+string name
		+string species
		+int age
		+dict preferences
		+update_profile(name, age, preferences)
		+get_preferences() dict
	}

	class CareTask {
		+int task_id
		+int pet_id
		+string task_type
		+datetime due_time
		+int priority
		+string status
		+mark_complete()
		+is_overdue(current_time) bool
	}

	class Scheduler {
		+list constraints
		+list prioritize_tasks(tasks)
		+list build_today_plan(tasks, current_time)
		+resolve_conflicts(tasks)
	}

	class PawPalApp {
		+list pets
		+list tasks
		+add_pet(pet)
		+schedule_task(task)
		+get_today_tasks(current_time) list
		+complete_task(task_id)
	}

	PawPalApp "1" o-- "many" Pet : manages
	PawPalApp "1" o-- "many" CareTask : stores
	PawPalApp "1" --> "1" Scheduler : uses
	Pet "1" --> "many" CareTask : has
```

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
