"""SOAP Summarize template.

Takes a conversation transcript and produces a concise SOAP-formatted
summary. Fewer intake fields since the goal is summarization rather
than guided data collection.
"""

TEMPLATE_NAME = "SOAP Summarize"
TEMPLATE_KEY = "soap_summarize"

FIELDS: dict[str, dict] = {
    "encounter_type": {
        "label": "Encounter Type",
        "description": "Type of visit (routine, emergency, follow-up, consultation)",
        "probe": "What type of visit was this?",
        "required": True,
    },
    "chief_complaint": {
        "label": "Chief Complaint",
        "description": "Patient's primary reason for the visit",
        "probe": "What was the main reason for the visit?",
        "required": True,
    },
    "key_findings": {
        "label": "Key Findings",
        "description": "Most significant clinical or diagnostic findings",
        "probe": "What were the key clinical findings?",
        "required": True,
    },
    "treatment_provided": {
        "label": "Treatment Provided",
        "description": "Procedures or treatment delivered during the visit",
        "probe": "What treatment was provided?",
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
