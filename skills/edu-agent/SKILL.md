---
name: "edu-agent"
description: "Compresses course catalogs and student progress. Invoke when creating personalized learning paths or summarizing curricula for learners/cohorts."
---

# Educational Agent

This skill builds efficient, personalized learning paths by compressing course catalogs and student progress data into a compact skill graph. Use it when:
- You need to transform large catalogs into a concise, prerequisite-aware map.
- You want to summarize a learner’s progress and produce next-step recommendations.
- You must generate individualized or cohort learning plans aligned to goals and constraints.

## Inputs
- Catalog (JSON)
  - courses: [{ id, title, topics: [str], outcomes: [str], prerequisites: [course_id or topic], modules: [{ id, title, topics }], hours }]
  - topics may repeat across courses; prerequisites may reference topics or courses.
- Learner progress (JSON)
  - mastery: { topic: 0–1 } or { topic: { level: 0–1, last_seen, evidence } }
  - completed_courses: [course_id]
  - preferences: { pace, interests: [topic], constraints: { max_hours_per_week, deadlines } }
- Targets (JSON, optional)
  - desired_outcomes: [str] or target_topics: [str]

## What It Does
1. Catalog Compression
   - Normalizes topics and deduplicates using basic canonicalization (lowercase, stemming-like heuristics).
   - Builds a topic-skill graph with edges for prerequisites and module coverage.
   - Collapses near-duplicate modules and aggregates per-topic coverage and estimated effort.
2. Progress Compression
   - Converts raw completions and evidence to a compact mastery vector per topic.
   - Infers gaps relative to prerequisites and targets.
3. Personalized Path Generation
   - Computes an ordered plan that satisfies prerequisites, fills gaps, and aligns with learner preferences and constraints.
   - Produces a sequence of modules (or topics) with estimated effort and rationale.

## Use Cases
- Individual plan: Given catalog + progress, output next 6–8 modules with rationale.
- Cohort plan: Aggregate progress and generate a shared baseline path plus individualized branches.
- Goal-oriented plan: Map to desired outcomes and backfill prerequisites efficiently.

## Guidelines
- Prefer topic-level planning for precision; map back to modules/courses for delivery.
- Keep plans short, iterative, and adaptive; recompute after each milestone.
- Respect constraints (hours, deadlines) and balance practice vs. new content.

## Example Input Shapes
Catalog:
```json
{
  "courses": [
    {
      "id": "cs101",
      "title": "Intro to CS",
      "topics": ["algorithms", "data structures", "complexity"],
      "prerequisites": [],
      "modules": [
        { "id": "cs101-m1", "title": "Algorithms Basics", "topics": ["algorithms"] },
        { "id": "cs101-m2", "title": "Data Structures", "topics": ["data structures"] }
      ],
      "hours": 12
    }
  ]
}
```

Progress:
```json
{
  "mastery": {
    "algorithms": 0.6,
    "data structures": 0.3
  },
  "completed_courses": [],
  "preferences": { "pace": "moderate", "interests": ["algorithms"], "constraints": { "max_hours_per_week": 8 } }
}
```

Targets:
```json
{ "target_topics": ["complexity"] }
```

## Output (Conceptual)
```json
{
  "plan": [
    {
      "module_id": "cs101-m2",
      "topics": ["data structures"],
      "estimated_hours": 4,
      "rationale": ["fills prerequisite gap for complexity", "aligns with pace and interests"]
    },
    {
      "module_id": "cs101-m1",
      "topics": ["algorithms"],
      "estimated_hours": 3,
      "rationale": ["raises mastery to threshold for advanced topics"]
    }
  ],
  "summary": { "gaps_closed": ["data structures"], "next_targets": ["complexity"] }
}
```

## Invocation Notes
- Invoke when asked to compress catalogs, summarize progress, or generate learning paths.
- Invoke before curriculum mapping or prerequisites analysis to build the skill graph.
- Re-invoke after progress updates to refresh the personalized plan.

