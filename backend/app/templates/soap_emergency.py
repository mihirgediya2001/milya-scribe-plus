"""SOAP Emergency Examination template.

SOAP-formatted note for urgent/emergency dental visits.
"""

TEMPLATE_NAME = "SOAP Emergency Examination"
TEMPLATE_KEY = "soap_emergency"

FIELDS: dict[str, dict] = {
    "chief_complaint": {
        "label": "Chief Complaint",
        "description": "Primary emergency concern and urgency",
        "probe": "What is the emergency? When did it start?",
        "required": True,
    },
    "pain_description": {
        "label": "Pain Description",
        "description": "Pain severity, character, location, and radiation",
        "probe": "Describe the pain: how severe, where exactly, and does it spread?",
        "required": True,
    },
    "onset_triggers": {
        "label": "Onset & Triggers",
        "description": "When the issue started and what provokes or relieves it",
        "probe": "What triggers the pain, and does anything relieve it?",
        "required": True,
    },
    "trauma_details": {
        "label": "Trauma Details",
        "description": "Mechanism of injury if trauma is involved",
        "probe": "Was there any injury? What happened?",
        "required": False,
    },
    "medical_allergies": {
        "label": "Medical History & Allergies",
        "description": "Relevant conditions, medications, drug allergies",
        "probe": "Any medical conditions, medications, or drug allergies?",
        "required": True,
    },
    "self_care_attempted": {
        "label": "Self-Care Attempted",
        "description": "Home remedies or OTC medications tried",
        "probe": "Have you tried anything for the pain or swelling?",
        "required": False,
    },
    "clinical_findings": {
        "label": "Clinical Findings",
        "description": "Emergency examination findings: swelling, mobility, fractures, vitality",
        "probe": "What does the emergency exam show?",
        "required": True,
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
