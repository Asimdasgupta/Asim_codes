import json
import re
from typing import Dict, List, Set

from .models import (
    Module,
    Course,
    Catalog,
    CompressedCatalog,
    CompressedTopic,
    Progress,
)


def normalize_topic(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"[\-_/]", " ", s)
    s = re.sub(r"[^a-z0-9\s]", "", s)
    s = re.sub(r"\s+", " ", s)
    tokens = s.split()
    norm_tokens: List[str] = []
    for t in tokens:
        if len(t) > 4 and t.endswith("s"):
            t = t[:-1]
        norm_tokens.append(t)
    return " ".join(norm_tokens)


def load_catalog(raw: Dict) -> Catalog:
    courses: List[Course] = []
    for c in raw.get("courses", []):
        modules = []
        for m in c.get("modules", []):
            modules.append(
                Module(
                    id=m.get("id") or f"{c.get('id','course')}-m{len(modules)+1}",
                    title=m.get("title", ""),
                    topics=[normalize_topic(t) for t in m.get("topics", [])],
                    hours=m.get("hours"),
                )
            )
        courses.append(
            Course(
                id=c.get("id", f"course-{len(courses)+1}"),
                title=c.get("title", ""),
                topics=[normalize_topic(t) for t in c.get("topics", [])],
                prerequisites=[normalize_topic(p) for p in c.get("prerequisites", [])],
                modules=modules,
                hours=c.get("hours"),
            )
        )
    return Catalog(courses=courses)


def compress_catalog(catalog: Catalog) -> CompressedCatalog:
    topics: Dict[str, CompressedTopic] = {}
    modules_index: Dict[str, Module] = {}
    edges: List[tuple] = []

    for course in catalog.courses:
        # Course-level topics coverage and prereqs
        for t in course.topics:
            nt = normalize_topic(t)
            topics.setdefault(nt, CompressedTopic(name=nt))
        for p in course.prerequisites:
            np = normalize_topic(p)
            topics.setdefault(np, CompressedTopic(name=np))
            for t in course.topics:
                nt = normalize_topic(t)
                if np != nt:
                    edges.append((nt, np))
                    topics[nt].prereq_topics.add(np)

        # Modules
        for m in course.modules:
            modules_index[m.id] = m
            mhours = m.hours if m.hours is not None else (course.hours or 0) / max(
                1, len(course.modules)
            )
            for t in m.topics or course.topics:
                nt = normalize_topic(t)
                ct = topics.setdefault(nt, CompressedTopic(name=nt))
                ct.modules.add(m.id)
                ct.coverage_hours += float(mhours or 0)

    # Deduplicate modules with identical topic sets
    seen_topics_sets: Dict[str, str] = {}  # fingerprint -> representative module id
    to_remove: Set[str] = set()
    for mid, mod in list(modules_index.items()):
        fp = "|".join(sorted(set(mod.topics)))
        if fp in seen_topics_sets:
            rep = seen_topics_sets[fp]
            # Redirect topic module mappings to representative
            for t in mod.topics:
                nt = normalize_topic(t)
                if mid in topics[nt].modules:
                    topics[nt].modules.remove(mid)
                    topics[nt].modules.add(rep)
            to_remove.add(mid)
        else:
            seen_topics_sets[fp] = mid
    for mid in to_remove:
        modules_index.pop(mid, None)

    return CompressedCatalog(topics=topics, modules=modules_index, topic_prereq_edges=edges)


def compress_progress(progress_raw: Dict, cc: CompressedCatalog) -> Progress:
    mastery_raw: Dict[str, float] = progress_raw.get("mastery", {})
    completed_courses: List[str] = progress_raw.get("completed_courses", [])
    preferences_raw = progress_raw.get("preferences", {}) or {}
    constraints_raw = preferences_raw.get("constraints", {}) or {}

    # Normalize mastery keys to catalog topics
    mastery: Dict[str, float] = {}
    for t in cc.topics.keys():
        mastery[t] = float(mastery_raw.get(t, mastery_raw.get(normalize_topic(t), 0.0)))

    # Boost mastery for topics covered by completed courses
    boost = 0.7
    for course_id in completed_courses:
        # naive: mark topics in modules that look like course_id prefix
        for mid, mod in cc.modules.items():
            if mid.startswith(course_id):
                for t in mod.topics:
                    mastery[t] = max(mastery.get(t, 0.0), boost)

    from .models import Preferences, Constraints
    prefs = Preferences(
        pace=preferences_raw.get("pace"),
        interests=[normalize_topic(i) for i in preferences_raw.get("interests", [])],
        constraints=Constraints(
            max_hours_per_week=constraints_raw.get("max_hours_per_week"),
            deadline_weeks=constraints_raw.get("deadline_weeks"),
        ),
    )

    return Progress(mastery=mastery, completed_courses=completed_courses, preferences=prefs)

