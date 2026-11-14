"""SOAP Comprehensive / Recall Examination template.

Structures the encounter note in the standard SOAP format
(Subjective, Objective, Assessment, Plan) for a comprehensive
or recall dental examination.
"""

TEMPLATE_NAME = "SOAP Comprehensive / Recall Examination"
TEMPLATE_KEY = "soap_comprehensive"

FIELDS: dict[str, dict] = {
    "chief_complaint": {
        "label": "Chief Complaint",
        "description": "Patient's primary reason for the visit",
        "probe": "What brings you in today?",
        "required": True,
    },
    "history_present_illness": {
        "label": "History of Present Illness",
        "description": "Onset, duration, character, triggers, and relieving factors",
        "probe": "Can you describe when this started and how it has changed?",
        "required": True,
    },
    "medical_history": {
        "label": "Medical / Dental History",
        "description": "Relevant medical conditions, medications, allergies, past dental history",
        "probe": "Any medical conditions, allergies, or changes to your medications?",
        "required": True,
    },
    "social_history": {
        "label": "Social History",
        "description": "Tobacco, alcohol, diet habits relevant to oral health",
        "probe": "Any tobacco use, and how would you describe your diet?",
        "required": False,
    },
    "oral_hygiene": {
        "label": "Oral Hygiene Habits",
        "description": "Brushing and flossing frequency, aids used",
        "probe": "How often do you brush and floss?",
        "required": True,
    },
    "vital_signs": {
        "label": "Vital Signs",
        "description": "Blood pressure, pulse, or other vitals if taken",
        "probe": "Were vitals recorded for this visit?",
        "required": False,
    },
    "clinical_findings": {
        "label": "Clinical Findings",
        "description": "Intraoral and extraoral examination findings",
        "probe": "What did the clinical examination reveal?",
        "required": True,
    },
    "radiographic_findings": {
        "label": "Radiographic Findings",
        "description": "Findings from radiographs, if taken",
        "probe": "Were X-rays taken? What do they show?",
        "required": False,
    },
}

NOTE_SECTIONS: list[tuple[str, str]] = [
    ("SUBJECTIVE", "subjective"),
    ("OBJECTIVE", "objective"),
    ("ASSESSMENT", "assessment"),
    ("PLAN", "plan"),
]


def render_note(note: dict[str, str]) -> str:
    """Format a note dict into SOAP plain-text layout."""
    lines: list[str] = []
    for heading, key in NOTE_SECTIONS:
        value = note.get(key, "Not discussed in this encounter.")
        lines.append(f"{heading}\n{value}\n")
    return "\n".join(lines).strip()
