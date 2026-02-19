from typing import Dict, List, Optional, Set, Tuple

from .models import CompressedCatalog, Progress


def _topo_order(missing: Set[str], prereqs: Dict[str, Set[str]]) -> List[str]:
    order: List[str] = []
    visited: Set[str] = set()
    temp: Set[str] = set()

    def visit(t: str):
        if t in visited:
            return
        if t in temp:
            return  # ignore cycles gracefully
        temp.add(t)
        for p in prereqs.get(t, set()):
            if p in missing:
                visit(p)
        temp.remove(t)
        visited.add(t)
        order.append(t)

    for t in list(missing):
        visit(t)
    return order


def _topic_prereqs_map(cc: CompressedCatalog) -> Dict[str, Set[str]]:
    m: Dict[str, Set[str]] = {}
    for t, ct in cc.topics.items():
        m[t] = set(ct.prereq_topics or [])
    return m


def _select_module_for_topic(cc: CompressedCatalog, topic: str, interests: List[str]) -> Optional[Tuple[str, float]]:
    # Pick module that covers topic, prefer those also covering interests, minimize hours
    best: Optional[Tuple[str, float, int]] = None  # (mid, hours, interest_overlap)
    for mid in cc.topics.get(topic, None).modules if topic in cc.topics else []:
        mod = cc.modules.get(mid)
        if not mod:
            continue
        hours = float(mod.hours or cc.topics[topic].coverage_hours or 1.0)
        overlap = len(set(mod.topics).intersection(set(interests)))
        score = (hours, -overlap)
        cand = (mid, hours, overlap)
        if best is None or (hours, -overlap) < (best[1], -best[2]):
            best = cand
    if best:
        return (best[0], best[1])
    return None


def plan_path(
    cc: CompressedCatalog,
    progress: Progress,
    target_topics: Optional[List[str]] = None,
    mastery_threshold: float = 0.7,
    max_hours: Optional[float] = None,
) -> Dict:
    # Determine missing topics relative to target or all topics
    mastery = progress.mastery
    interests = progress.preferences.interests or []
    if target_topics:
        targets = {t for t in [t for t in target_topics]}
        targets = {t for t in [t.lower().strip() for t in targets]}
    else:
        targets = set(cc.topics.keys())

    prereqs = _topic_prereqs_map(cc)
    # Compute closure of prerequisites for targets
    required: Set[str] = set()
    def add_with_prereqs(t: str):
        nt = t
        required.add(nt)
        for p in prereqs.get(nt, set()):
            if p not in required:
                add_with_prereqs(p)
    for t in targets:
        add_with_prereqs(t)

    missing: Set[str] = {t for t in required if mastery.get(t, 0.0) < mastery_threshold}
    ordered_topics = _topo_order(missing, prereqs)

    plan = []
    total_hours = 0.0
    hours_budget = max_hours or progress.preferences.constraints.max_hours_per_week

    for t in ordered_topics:
        sel = _select_module_for_topic(cc, t, interests)
        if not sel:
            continue
        mid, hours = sel
        if hours_budget is not None and total_hours + hours > hours_budget:
            break
        plan.append(
            {
                "module_id": mid,
                "topics": [t],
                "estimated_hours": round(hours, 2),
                "rationale": [
                    "fills prerequisite gap" if t in prereqs.get(t, set()) else "builds target mastery",
                    "aligns with interests" if any(i in cc.modules[mid].topics for i in interests) else "neutral alignment",
                ],
            }
        )
        total_hours += hours

    return {
        "plan": plan,
        "summary": {
            "topics_considered": len(required),
            "topics_planned": len(ordered_topics),
            "estimated_total_hours": round(total_hours, 2),
        },
    }

