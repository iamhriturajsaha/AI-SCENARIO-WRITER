from pydantic import BaseModel, Field
from typing import Literal
class ScenarioInput(BaseModel):
    icp_type: Literal["high_wage", "low_wage"] = Field(
        description="User persona type. high_wage = tech professional, low_wage = gig/service worker"
    )
    milestone_code: str = Field(
        pattern=r"^M0[1-7]$",
        description="Career milestone code from M01 (beginner) to M07 (advanced)"
    )
    skill_target: str = Field(
        description="The specific skill this scenario should train, e.g. 'stakeholder_communication'"
    )
    language: Literal["en", "hi"] = Field(
        description="Output language. 'en' = English, 'hi' = Hindi (Devanagari)"
    )
class Scene(BaseModel):
    setting: str = Field(description="Where the scenario takes place")
    time: str = Field(description="When the scenario takes place")
    context: str = Field(description="What just happened to create this situation")
class Character(BaseModel):
    name: str = Field(description="Character's name, culturally appropriate for the ICP")
    role: str = Field(description="Character's professional role/title")
    mood: str = Field(description="Character's current emotional state")
class StrategyChip(BaseModel):
    id: str = Field(description="Unique identifier like 'chip_1', 'chip_2', 'chip_3'")
    label: str = Field(description="Short label for the strategy, e.g. 'Direct Confrontation'")
    philosophy: str = Field(
        description="WHY this strategy works — the underlying principle, not just what to do"
    )
class Rubric(BaseModel):
    communication: int = Field(ge=0, le=100, description="How well the user communicates")
    composure: int = Field(ge=0, le=100, description="How well the user keeps composure under pressure")
    clarity: int = Field(ge=0, le=100, description="How clear and structured the user's response is")
    strategy: int = Field(ge=0, le=100, description="How strategically sound the user's approach is")
    outcome: int = Field(ge=0, le=100, description="How effective the overall outcome is")
class ScenarioOutput(BaseModel):
    episode_title: str = Field(description="Catchy, specific title for the scenario episode")
    scene: Scene = Field(description="Scene setup with setting, time, and context")
    characters: list[Character] = Field(
        min_length=2,
        description="Characters involved in the scenario (minimum 2)"
    )
    antagonist_opening_line: str = Field(
        min_length=15,
        description="The line that creates genuine tension — must be specific, not generic"
    )
    strategy_chips: list[StrategyChip] = Field(
        min_length=3,
        max_length=3,
        description="Exactly 3 meaningfully different response strategies"
    )
    success_criteria: list[str] = Field(
        min_length=2,
        description="What constitutes success in this scenario"
    )
    rubric: Rubric = Field(description="Scoring rubric with 5 axes, each 0-100")
    transfer_targets: list[str] = Field(
        min_length=1,
        description="Real-world skills this scenario teaches"
    )
MILESTONE_MAP = {
    "M01": {
        "level": "beginner",
        "label": "First Steps",
        "description": "Just starting out, learning fundamentals, building confidence",
        "difficulty_multiplier": 0.6,
    },
    "M02": {
        "level": "beginner-intermediate",
        "label": "Building Habits",
        "description": "Developing consistent work habits, facing first real challenges",
        "difficulty_multiplier": 0.7,
    },
    "M03": {
        "level": "intermediate",
        "label": "Real Challenges",
        "description": "Handling genuine workplace conflicts and multi-stakeholder situations",
        "difficulty_multiplier": 0.8,
    },
    "M04": {
        "level": "intermediate-advanced",
        "label": "Growing Responsibility",
        "description": "Taking ownership of outcomes, managing ambiguity",
        "difficulty_multiplier": 0.85,
    },
    "M05": {
        "level": "advanced",
        "label": "Leadership Moments",
        "description": "Leading others, making high-stakes decisions, navigating politics",
        "difficulty_multiplier": 0.9,
    },
    "M06": {
        "level": "advanced",
        "label": "Strategic Thinking",
        "description": "Balancing competing priorities, influencing without authority",
        "difficulty_multiplier": 0.95,
    },
    "M07": {
        "level": "expert",
        "label": "Mastery",
        "description": "Mentoring others, handling crisis situations, systemic problem-solving",
        "difficulty_multiplier": 1.0,
    },
}