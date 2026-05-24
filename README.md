# 📝AI Scenario Writer
> AI-powered workplace scenario generator for a career upskilling platform.  
> Generates vivid, ICP-differentiated scenarios with genuine tension, diverse strategies and calibrated rubrics.

## Quick Start
### 1. Clone & Install

```bash
git clone https://github.com/iamhriturajsaha/AI-SCENARIO-WRITER.git
cd AI-SCENARIO-WRITER
pip install -r requirements.txt
```

### 2. Set API Key
```bash
# Edit .env and set :-
GROQ_API_KEY=your-key-here
```

### 3. Run on a single test case
```bash
# ICP-A example (high_wage, English)
python -m src.main --input "Test Cases/Inputs/icp_a_01.json"

# ICP-B example (low_wage, Hindi)
python -m src.main --input "Test Cases/Inputs/icp_b_01.json"
```

### 4. Run all 10 test cases
```bash
python run_tests.py
```

---
## Architecture
```
Input JSON → Prompt Chain → Validated JSON Output
                │
                ├── Stage 1 - Build context-rich user prompt.
                ├── Stage 2 - Call Groq Llama 3 70B → get scenario JSON.
                └── Stage 3 - Validate schema + quality → auto-repair if needed.
```

### Key design decisions
| Decision | Rationale |
|----------|-----------|
| **Pydantic v2 schema enforcement** | Zero tolerance for missing/extra fields or wrong types |
| **Quality validator with auto-repair** | Catches generic antagonist lines, similar strategy chips, flat rubrics |
| **Explicit ICP forking in system prompt** | Not left to model inference — tech vs. service contexts are hard-coded |
| **Anti-pattern examples in prompt** | Shows the model exactly what NOT to produce |
| **Max 2 repair retries** | Balances quality with API cost/latency |

## Input Schema
```json
{
  "icp_type": "high_wage | low_wage",
  "milestone_code": "M01 through M07",
  "skill_target": "e.g. stakeholder_communication",
  "language": "en | hi"
}
```

## Output Schema
```json
{
  "episode_title": "string",
  "scene": { "setting": "string", "time": "string", "context": "string" },
  "characters": [{ "name": "string", "role": "string", "mood": "string" }],
  "antagonist_opening_line": "string (15+ words, specific tension)",
  "strategy_chips": [
    { "id": "chip_1", "label": "string", "philosophy": "string (WHY it works)" },
    { "id": "chip_2", "label": "string", "philosophy": "string" },
    { "id": "chip_3", "label": "string", "philosophy": "string" }
  ],
  "success_criteria": ["string"],
  "rubric": {
    "communication": 0-100,
    "composure": 0-100,
    "clarity": 0-100,
    "strategy": 0-100,
    "outcome": 0-100
  },
  "transfer_targets": ["string"]
}
```

## Test Cases
| # | File | ICP | Milestone | Skill Target | Language |
|---|------|-----|-----------|-------------|----------|
| 1 | icp_a_01 | high_wage | M01 | stakeholder_communication | en |
| 2 | icp_a_02 | high_wage | M03 | conflict_resolution | en |
| 3 | icp_a_03 | high_wage | M05 | technical_leadership | en |
| 4 | icp_a_04 | high_wage | M02 | time_management | en |
| 5 | icp_a_05 | high_wage | M07 | cross_team_collaboration | en |
| 6 | icp_b_01 | low_wage | M01 | customer_handling | hi |
| 7 | icp_b_02 | low_wage | M02 | workplace_communication | hi |
| 8 | icp_b_03 | low_wage | M04 | problem_solving | hi |
| 9 | icp_b_04 | low_wage | M03 | professional_etiquette | hi |
| 10 | icp_b_05 | low_wage | M05 | negotiation | hi |

## Model
- **Provider -** Groq
- **Model -** llama-3.1-8b-instant
- **Max tokens -** 4096

## Challenges & Key Solutions
### 1. Strategy & Philosophy Diversity
* **Challenge -** LLMs generate repetitive options (e.g., three ways to apologize) or copy-paste phrasing templates.
* **Solution -** Custom token overlap validator using Jaccard similarity (excluding stop words) to reject overlaps >60% and enforce distinct strategic/psychological philosophies.

### 2. Lazy Flat Rubric Traps
* **Challenge -** Models default to identical scores (e.g., all 50s) across all rubric dimensions.
* **Solution -** Strict rubric variance check ensuring varied weights that align with the specific scenario's learning goal.

### 3. Generic Opening Lines
* **Challenge -** Overuse of immersion-breaking clichés like *"We need to talk about your performance."*
* **Solution -** Regex-based antagonist line filter (`GENERIC_PATTERNS`) combined with a word-count threshold to mandate context-rich, high-tension lines.

### 4. Tech vs. Service ICP Drift
* **Challenge -** Keeping corporate tech terms (like *sprint*, *deploy*) out of gig/service worker contexts and vice versa.
* **Solution -** Automated ICP keyword checks that validate domain-specific terminology for both personas.

### 5. API Flakiness & Rate Limits
* **Challenge -** Transient API timeouts and HTTP `429` rate limits from Groq under load.
* **Solution -** A resilient retry-and-backoff loop handling retryable errors (500, 503, 429) up to 5 times.
