"""Recall (routine check-up) examination template.

For periodic recall visits: oral health status since last visit,
periodontal assessment, preventive care, and next recall schedule.
"""

TEMPLATE_NAME = "Recall Examination"
TEMPLATE_KEY = "recall_exam"

FIELDS: dict[str, dict] = {
    "interval_history": {
        "label": "Interval History",
        "description": "Changes in oral health or complaints since the last visit",
        "probe": "Any new dental concerns or changes since your last visit?",
        "required": True,
    },
    "medical_update": {
        "label": "Medical Update",
        "description": "Changes to medications, medical conditions, or allergies",
        "probe": "Any changes in your health, medications, or allergies since we last saw you?",
        "required": True,
    },
    "oral_hygiene_habits": {
        "label": "Oral Hygiene Habits",
        "description": "Current brushing, flossing, and interdental care routine",
        "probe": "How has your brushing and flossing routine been?",
        "required": True,
    },
    "periodontal_status": {
        "label": "Periodontal Status",
        "description": "Gum health, probing depths, bleeding on probing",
        "probe": "Have you noticed any gum bleeding, sensitivity, or recession?",
        "required": True,
    },
    "caries_risk": {
        "label": "Caries Risk Assessment",
        "description": "Diet, dry mouth, visible decay, or new restorations needed",
        "probe": "Any changes in diet, dry mouth, or sensitivity to sweets?",
        "required": True,
    },
    "existing_restorations": {
        "label": "Existing Restorations",
        "description": "Condition of current fillings, crowns, or prosthetics",
        "probe": "Any issues with your current fillings, crowns, or dental work?",
        "required": False,
    },
    "radiographic_findings": {
        "label": "Radiographic Findings",
        "description": "Findings from any radiographs taken during this visit",
        "probe": "Were any X-rays taken today? Any notable findings?",
        "required": False,
    },
    "patient_concerns": {
        "label": "Patient Concerns",
        "description": "Any cosmetic or functional concerns raised by the patient",
        "probe": "Anything else about your teeth or smile you'd like to discuss?",
        "required": False,
    },
}

NOTE_SECTIONS: list[tuple[str, str]] = [
    ("INTERVAL HISTORY", "interval_history"),
    ("MEDICAL UPDATE", "medical_update"),
    ("ORAL HYGIENE ASSESSMENT", "oral_hygiene_assessment"),
    ("PERIODONTAL STATUS", "periodontal_status"),
    ("CARIES RISK", "caries_risk"),
    ("CLINICAL EXAMINATION", "clinical_examination"),
    ("RADIOGRAPHIC FINDINGS", "radiographic_findings"),
    ("TREATMENT COMPLETED", "treatment_completed"),
    ("PREVENTIVE CARE PLAN", "preventive_care_plan"),
    ("NEXT RECALL", "next_recall"),
]


def render_note(note: dict[str, str]) -> str:
    """Format a note dict into the Milya-style plain-text layout."""
    lines: list[str] = []
    for heading, key in NOTE_SECTIONS:
        value = note.get(key, "Not discussed in this encounter.")
        lines.append(f"{heading}\n{value}\n")
    return "\n".join(lines).strip()
