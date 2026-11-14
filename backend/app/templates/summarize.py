"""Summarize template.

Produces a brief, plain-language summary of the dental encounter.
Minimal intake fields -- the goal is a concise narrative summary
rather than structured clinical documentation.
"""

TEMPLATE_NAME = "Summarize"
TEMPLATE_KEY = "summarize"

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
        "description": "Most significant findings from the encounter",
        "probe": "What were the key findings?",
        "required": False,
    },
}

NOTE_SECTIONS: list[tuple[str, str]] = [
    ("ENCOUNTER SUMMARY", "encounter_summary"),
    ("KEY FINDINGS", "key_findings"),
    ("TREATMENT PROVIDED", "treatment_provided"),
    ("FOLLOW-UP", "follow_up"),
]


def render_note(note: dict[str, str]) -> str:
    """Format a note dict into the Milya-style plain-text layout."""
    lines: list[str] = []
    for heading, key in NOTE_SECTIONS:
        value = note.get(key, "Not discussed in this encounter.")
        lines.append(f"{heading}\n{value}\n")
    return "\n".join(lines).strip()
