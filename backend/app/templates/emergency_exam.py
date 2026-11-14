"""Emergency dental examination template.

Focused on acute/urgent dental issues: pain triage, immediate findings,
and emergency treatment planning.
"""

TEMPLATE_NAME = "Emergency Examination"
TEMPLATE_KEY = "emergency_exam"

FIELDS: dict[str, dict] = {
    "chief_complaint": {
        "label": "Chief Complaint",
        "description": "Primary emergency concern and how it started",
        "probe": "What happened? Can you describe the emergency?",
        "required": True,
    },
    "pain_severity": {
        "label": "Pain Severity",
        "description": "Pain level on a 0-10 scale and its character",
        "probe": "On a scale of 0-10, how bad is the pain right now?",
        "required": True,
    },
    "onset_timing": {
        "label": "Onset & Timing",
        "description": "When the issue started and any triggering event",
        "probe": "When did this start? Did anything specific trigger it?",
        "required": True,
    },
    "swelling_bleeding": {
        "label": "Swelling / Bleeding",
        "description": "Presence and location of swelling, bleeding, or discharge",
        "probe": "Is there any swelling, bleeding, or discharge?",
        "required": True,
    },
    "trauma_history": {
        "label": "Trauma History",
        "description": "Whether trauma or injury was involved",
        "probe": "Was there any injury or trauma to the area?",
        "required": True,
    },
    "self_treatment": {
        "label": "Self-Treatment",
        "description": "Any medications or home remedies tried",
        "probe": "Have you taken anything for the pain or tried any home remedies?",
        "required": False,
    },
    "allergies": {
        "label": "Allergies & Medications",
        "description": "Drug allergies and current medications relevant to emergency care",
        "probe": "Any drug allergies or medications I should know about before treatment?",
        "required": True,
    },
    "medical_conditions": {
        "label": "Relevant Medical Conditions",
        "description": "Conditions that affect emergency dental treatment (bleeding disorders, etc.)",
        "probe": "Any medical conditions like diabetes, blood thinners, or heart issues?",
        "required": True,
    },
}

NOTE_SECTIONS: list[tuple[str, str]] = [
    ("CHIEF COMPLAINT", "chief_complaint"),
    ("PAIN ASSESSMENT", "pain_assessment"),
    ("CLINICAL FINDINGS", "clinical_findings"),
    ("EMERGENCY DIAGNOSIS", "emergency_diagnosis"),
    ("IMMEDIATE TREATMENT", "immediate_treatment"),
    ("MEDICATIONS PRESCRIBED", "medications_prescribed"),
    ("FOLLOW-UP PLAN", "follow_up_plan"),
]


def render_note(note: dict[str, str]) -> str:
    """Format a note dict into the Milya-style plain-text layout."""
    lines: list[str] = []
    for heading, key in NOTE_SECTIONS:
        value = note.get(key, "Not discussed in this encounter.")
        lines.append(f"{heading}\n{value}\n")
    return "\n".join(lines).strip()
