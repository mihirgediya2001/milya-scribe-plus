"""Comprehensive dental examination template.

Defines the fields a complete exam note should contain, together with the
clarifying question the agent asks when a field is missing from the transcript.
"""

TEMPLATE_NAME = "Comprehensive Examination"
TEMPLATE_KEY = "comprehensive_exam"

FIELDS: dict[str, dict] = {
    "chief_complaint": {
        "label": "Chief Complaint",
        "description": "Patient's primary reason for the visit and when it started",
        "probe": "What brings you in today? Can you describe the main issue?",
        "required": True,
    },
    "pain_character": {
        "label": "Pain Character",
        "description": "Type and nature of the pain (sharp, dull, throbbing, aching)",
        "probe": "Can you describe the pain? Is it sharp, dull, throbbing, or more of an ache?",
        "required": True,
    },
    "pain_triggers": {
        "label": "Pain Triggers",
        "description": "What triggers or worsens the pain",
        "probe": "What makes the pain worse? Cold drinks, hot food, sweets, or biting down?",
        "required": True,
    },
    "pain_duration": {
        "label": "Pain Duration & Onset",
        "description": "When the pain started and how long each episode lasts",
        "probe": "How long have you had this? When the pain comes, does it go away quickly or linger?",
        "required": True,
    },
    "night_pain": {
        "label": "Night Pain",
        "description": "Whether the pain occurs at night or wakes the patient",
        "probe": "Does the pain ever wake you up at night or keep you from sleeping?",
        "required": True,
    },
    "swelling": {
        "label": "Swelling & Redness",
        "description": "Visible swelling, redness, or tenderness in the area",
        "probe": "Have you noticed any swelling, redness, or tenderness around that area?",
        "required": True,
    },
    "oral_hygiene": {
        "label": "Oral Hygiene",
        "description": "Brushing, flossing, and professional cleaning habits",
        "probe": "How often do you brush and floss? When was your last professional cleaning?",
        "required": True,
    },
    "diet_habits": {
        "label": "Diet & Habits",
        "description": "Recent diet, hard or sugary foods, grinding or clenching",
        "probe": "Have you had anything particularly hard, sticky, or sugary recently? Do you grind your teeth?",
        "required": False,
    },
    "previous_treatment": {
        "label": "Previous Treatment",
        "description": "Recent dental work or medications taken for this issue",
        "probe": "Have you had any recent dental work on this tooth, or taken anything for the pain?",
        "required": True,
    },
    "medical_history": {
        "label": "Medical History",
        "description": "Relevant medical conditions, allergies, or current medications",
        "probe": "Any medical conditions, allergies, or medications I should know about?",
        "required": True,
    },
}

# Sections that appear in the rendered note (some aggregate multiple fields).
NOTE_SECTIONS: list[tuple[str, str]] = [
    ("CHIEF COMPLAINT", "chief_complaint"),
    ("PAIN HISTORY", "pain_history"),
    ("MEDICAL HISTORY", "medical_history"),
    ("ORAL HYGIENE", "oral_hygiene"),
    ("DIET & HABITS", "diet_habits"),
    ("PREVIOUS TREATMENT", "previous_treatment"),
    ("CLINICAL EXAMINATION", "clinical_examination"),
    ("DIAGNOSIS", "diagnosis"),
    ("TREATMENT PLAN", "treatment_plan"),
    ("NEXT APPOINTMENT", "next_appointment"),
]


def render_note(note: dict[str, str]) -> str:
    """Format a note dict into the Milya-style plain-text layout."""
    lines: list[str] = []
    for heading, key in NOTE_SECTIONS:
        value = note.get(key, "Not discussed in this encounter.")
        lines.append(f"{heading}\n{value}\n")
    return "\n".join(lines).strip()
