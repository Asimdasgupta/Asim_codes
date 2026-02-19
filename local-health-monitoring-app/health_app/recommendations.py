from __future__ import annotations

from .features import bmi_from_profile


def classify_bmi(bmi: float | None) -> str | None:
    if bmi is None:
        return None
    if bmi < 18.5:
        return "underweight"
    if bmi < 25.0:
        return "normal"
    if bmi < 30.0:
        return "overweight"
    return "obese"


def classify_bp(sys: float | None, dia: float | None) -> str | None:
    if sys is None or dia is None:
        return None
    if sys < 120 and dia < 80:
        return "normal"
    if 120 <= sys < 130 and dia < 80:
        return "elevated"
    if (130 <= sys < 140) or (80 <= dia < 90):
        return "hypertension_stage_1"
    if sys >= 140 or dia >= 90:
        return "hypertension_stage_2"
    return "unknown"


def classify_sugar(sugar: float | None) -> str | None:
    if sugar is None:
        return None
    if sugar < 100:
        return "normal"
    if sugar < 126:
        return "prediabetes"
    return "diabetes_range"


def classify_activity(steps: int | None) -> str | None:
    if steps is None:
        return None
    if steps < 5000:
        return "low"
    if steps < 8000:
        return "moderate"
    return "high"


def build_recommendations(profile: dict, latest_entry: dict | None, model_score: float | None) -> list[dict]:
    recos: list[dict] = []

    bmi = bmi_from_profile(profile)
    bmi_class = classify_bmi(bmi)
    if bmi_class == "underweight":
        recos.append(
            {
                "title": "Support healthy weight gain",
                "priority": "medium",
                "text": "Add nutrient-dense foods and consider strength training. If weight loss is unintentional, talk to a clinician.",
                "rationale": "BMI suggests underweight.",
            }
        )
    elif bmi_class == "overweight":
        recos.append(
            {
                "title": "Aim for gradual weight improvement",
                "priority": "medium",
                "text": "Try consistent activity and reduce sugary drinks/ultra-processed snacks. Small weekly changes work best.",
                "rationale": "BMI suggests overweight.",
            }
        )
    elif bmi_class == "obese":
        recos.append(
            {
                "title": "Prioritize sustainable lifestyle changes",
                "priority": "high",
                "text": "Focus on daily movement, balanced meals, and sleep. If possible, discuss a plan with a healthcare professional.",
                "rationale": "BMI suggests obesity.",
            }
        )

    bp_sys = latest_entry.get("bp_systolic") if latest_entry else profile.get("bp_systolic")
    bp_dia = latest_entry.get("bp_diastolic") if latest_entry else profile.get("bp_diastolic")
    bp_class = classify_bp(
        float(bp_sys) if bp_sys is not None else None,
        float(bp_dia) if bp_dia is not None else None,
    )
    if bp_class in {"elevated", "hypertension_stage_1", "hypertension_stage_2"}:
        prio = "high" if bp_class == "hypertension_stage_2" else "medium"
        recos.append(
            {
                "title": "Support healthy blood pressure",
                "priority": prio,
                "text": "Reduce excess salt, stay active, and limit alcohol. If readings are consistently high, talk to a clinician.",
                "rationale": f"BP category: {bp_class.replace('_', ' ')}.",
            }
        )

    sugar = latest_entry.get("sugar_mg_dl") if latest_entry else profile.get("sugar_mg_dl")
    sugar_class = classify_sugar(float(sugar) if sugar is not None else None)
    if sugar_class in {"prediabetes", "diabetes_range"}:
        prio = "high" if sugar_class == "diabetes_range" else "medium"
        recos.append(
            {
                "title": "Support healthy blood sugar",
                "priority": prio,
                "text": "Choose high-fiber meals, reduce sugary drinks, and add short walks after meals.",
                "rationale": f"Sugar category: {sugar_class.replace('_', ' ')}.",
            }
        )

    steps = None
    if latest_entry is not None:
        steps = latest_entry.get("steps")
    activity_class = classify_activity(int(steps) if steps is not None else None)
    if activity_class == "low":
        recos.append(
            {
                "title": "Increase daily activity",
                "priority": "medium",
                "text": "Start with a 10–20 minute walk and build up. Try to move a little every hour.",
                "rationale": "Recent steps suggest low activity.",
            }
        )

    if model_score is not None:
        if model_score >= 0.75:
            recos.append(
                {
                    "title": "Higher risk signal detected",
                    "priority": "high",
                    "text": "Your recent summary signals look higher-risk. Consider reviewing BP/sugar readings and consult a clinician if concerned.",
                    "rationale": f"Model risk score: {model_score:.2f}.",
                }
            )
        elif model_score >= 0.5:
            recos.append(
                {
                    "title": "Moderate risk signal detected",
                    "priority": "medium",
                    "text": "Focus on sleep, hydration, and steady activity. Re-check BP/sugar if you track them.",
                    "rationale": f"Model risk score: {model_score:.2f}.",
                }
            )

    if not recos:
        recos.append(
            {
                "title": "Keep building consistent habits",
                "priority": "low",
                "text": "Log your daily check-ins and aim for balanced sleep, movement, and nutrition.",
                "rationale": "Not enough signals yet to personalize strongly.",
            }
        )

    return recos

