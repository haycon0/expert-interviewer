# Original handoff doc

This is the design spec the prototype was built from. The content is unchanged; a few JSON examples are reformatted onto single lines. It was generated with an AI assistant during brainstorming (GitHub Copilot in this case, though any capable AI assistant could produce one). See [DEVELOPMENT.md](DEVELOPMENT.md) for how the build departed from it.

---

# LangGraph Implementation Handoff
## Project: Expert Interviewer Multi-Agent System

### Project Vision

Build a multi-agent interview simulation platform that allows a user to:

1. Select an expert.
2. Provide interview objectives and background information.
3. Automatically research the expert.
4. Generate a synthetic expert persona.
5. Conduct a realistic interview with the synthetic expert.
6. Generate a customized grading rubric.
7. Grade the interview when complete.
8. Provide coaching and improvement recommendations.

The system should use LangGraph for orchestration and maintain state throughout the interview lifecycle.

---

# High-Level Architecture

```text
                     User
                       │
                       ▼
       Expert Interviewer Master Agent
                       │
      ┌────────────────┼────────────────┐
      │                │                │
      ▼                ▼                ▼
Research Agent   Criteria Agent   Session Manager
      │                │                │
      └──────────┬─────┘                │
                 ▼                      │
          Interview Context             │
                 │                      │
                 ▼                      │
       Synthetic Expert Agent           │
                 │                      │
                 │ <multi-turn chat>    │
                 │                      │
                 ▼                      │
            End Interview               │
                 │                      │
                 ▼                      ▼
             Grader Agent      Transcript Store
                 │
                 ▼
             Assessment
```

---

# Primary Goal

The user should feel like they are interviewing a real expert while receiving professional feedback on:

- Question quality
- Topic coverage
- Follow-up questions
- Critical thinking
- Interview technique

---

# Technical Stack

Preferred:

- LangGraph
- LangChain
- Azure OpenAI GPT-4o
- FastAPI
- PostgreSQL
- Redis
- Microsoft Dataverse (optional)
- Azure AI Search (optional)
- Azure Blob Storage (optional)

---

# Core Agents

## 1. Master Agent

Responsibilities:

- Entry point
- Workflow orchestration
- Agent coordination
- Session lifecycle management

Inputs:

```json
{
  "expert_name": "",
  "user_outline": "",
  "persona": "",
  "interview_objectives": ""
}
```

Outputs:

```json
{
  "research_package": {},
  "rubric": {},
  "session_id": ""
}
```

Master Agent should never directly answer expert questions.

It should coordinate specialist agents.

---

## 2. Research Agent

Purpose:

Research the requested expert and generate a structured profile.

Inputs:

```json
{
  "expert_name": "",
  "user_outline": ""
}
```

Tasks:

- Gather biography
- Collect major works
- Identify frameworks
- Identify important concepts
- Identify criticisms
- Generate recommended interview areas

Output:

```json
{
  "expert_name": "",
  "biography": "",
  "major_works": [],
  "frameworks": [],
  "concepts": [],
  "criticisms": [],
  "recommended_topics": [],
  "source_material": []
}
```

The output should be structured data.

No narrative responses.

---

## 3. Criteria Creator Agent

Purpose:

Create a grading rubric tailored to the expert and interview objectives.

Inputs:

```json
{
  "research_package": {},
  "persona": "",
  "user_objectives": ""
}
```

Output:

```json
{
  "rubric": [
    { "name": "Knowledge Coverage", "weight": 25 },
    { "name": "Question Depth", "weight": 20 },
    { "name": "Follow-Up Quality", "weight": 20 },
    { "name": "Critical Thinking", "weight": 15 },
    { "name": "Interview Flow", "weight": 10 },
    { "name": "Application", "weight": 10 }
  ]
}
```

Should also generate scoring guidance.

---

## 4. Synthetic Expert Agent

Purpose:

Simulate the expert.

Inputs:

```json
{
  "research_package": {},
  "persona_profile": {},
  "user_outline": {}
}
```

Behavior:

- Speak as the expert
- Remain in character
- Use research package as primary context
- Blend in persona traits
- Never reveal system instructions
- Admit uncertainty if information is unavailable

Must support unlimited conversational turns.

---

## 5. Grader Agent

Purpose:

Evaluate interview quality.

Inputs:

```json
{
  "rubric": {},
  "transcript": []
}
```

Outputs:

```json
{
  "overall_score": 92,
  "letter_grade": "A",
  "category_scores": [],
  "strengths": [],
  "weaknesses": [],
  "missed_opportunities": [],
  "recommended_questions": [],
  "coaching_recommendations": []
}
```

---

# Persona Library

Implement as configuration-driven.

Initial personas:

```json
[
  { "name": "Academic Professor", "traits": ["Analytical", "Detailed", "Socratic"] },
  { "name": "Executive Leader", "traits": ["Strategic", "Concise", "Business Focused"] },
  { "name": "Friendly Mentor", "traits": ["Supportive", "Encouraging", "Patient"] },
  { "name": "Military Commander", "traits": ["Disciplined", "Direct", "Results-Oriented"] },
  { "name": "Startup Founder", "traits": ["Innovative", "Fast Moving", "Growth Focused"] }
]
```

Design so new personas can be added without code changes.

---

# State Management

Create a central interview state object.

```python
class InterviewState(TypedDict):
    session_id: str
    expert_name: str
    persona_name: str
    user_outline: str

    research_package: dict
    rubric: dict

    interview_started: bool
    interview_complete: bool

    transcript: list

    final_assessment: dict
```

---

# Transcript Structure

Every exchange should be persisted.

```json
{ "speaker": "user", "timestamp": "", "message": "" }
```

```json
{ "speaker": "expert", "timestamp": "", "message": "" }
```

Transcript should be append-only.

No summarization until grading.

---

# LangGraph Design

Recommended graph:

```text
START
  │
  ▼
Master Initialization
  │
  ▼
Research Agent
  │
  ▼
Criteria Agent
  │
  ▼
Create Session
  │
  ▼
Interview Loop
  │
  ├── User Continues
  │
  │      ▼
  │  Synthetic Expert
  │      │
  │      └── back to Interview Loop
  │
  └── End Interview
         │
         ▼
     Grader Agent
         │
         ▼
        END
```

---

# LangGraph Node Definitions

Nodes:

```python
initialize_session
run_research
generate_rubric
start_interview
expert_response
check_interview_end
grade_interview
finalize_session
```

---

# Persistence Requirements

Must persist:

- Session metadata
- Research package
- Rubric
- Transcript
- Final assessment

Storage options:

Preferred:
- PostgreSQL

Optional:
- Dataverse
- Cosmos DB

---

# API Endpoints

Suggested:

```text
POST /session/create
POST /session/{id}/message
POST /session/{id}/end
GET /session/{id}
GET /session/{id}/results
```

---

# Success Criteria

MVP Success:

1. User creates expert interview.
2. Research package generated.
3. Rubric generated.
4. Synthetic expert conducts interview.
5. Transcript captured.
6. Interview can be ended.
7. Grading produced.
8. Results returned.

---

# Future Enhancements

Phase 2:

- Voice interviews
- Multi-expert panels
- Adaptive rubrics
- Web research tools
- Citation generation
- Teams integration
- Copilot Studio integration
- Dataverse integration
- Analytics dashboard

---

# Development Priority Order

1. Define InterviewState.
2. Build LangGraph orchestration.
3. Build Research Agent.
4. Build Criteria Creator Agent.
5. Build Synthetic Expert Agent.
6. Build transcript persistence.
7. Build Grader Agent.
8. Expose FastAPI endpoints.
9. Add UI.
10. Add enterprise integrations.

Deliver an MVP first with mocked storage and a single LLM provider before adding Azure services and Microsoft integrations.
