from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set


@dataclass
class Module:
    id: str
    title: str
    topics: List[str]
    hours: Optional[float] = None


@dataclass
class Course:
    id: str
    title: str
    topics: List[str]
    prerequisites: List[str]
    modules: List[Module]
    hours: Optional[float] = None


@dataclass
class Catalog:
    courses: List[Course]


@dataclass
class Constraints:
    max_hours_per_week: Optional[float] = None
    deadline_weeks: Optional[int] = None


@dataclass
class Preferences:
    pace: Optional[str] = None
    interests: List[str] = field(default_factory=list)
    constraints: Constraints = field(default_factory=Constraints)


@dataclass
class Progress:
    mastery: Dict[str, float]
    completed_courses: List[str] = field(default_factory=list)
    preferences: Preferences = field(default_factory=Preferences)


@dataclass
class CompressedTopic:
    name: str
    modules: Set[str] = field(default_factory=set)
    prereq_topics: Set[str] = field(default_factory=set)
    coverage_hours: float = 0.0


@dataclass
class CompressedCatalog:
    topics: Dict[str, CompressedTopic]  # normalized topic -> data
    modules: Dict[str, Module]          # module_id -> module
    topic_prereq_edges: List[tuple]     # (topic, prereq_topic)

