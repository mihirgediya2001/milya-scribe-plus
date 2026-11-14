"""Clarifying agent and note generator.

Two LLM calls power the scribe:

1. **analyze** -- given the running transcript, extract what's known, flag
   what's missing, produce a best-effort note, and suggest clarifying questions.
2. **generate_final_note** -- produce a polished, structured note suitable for
   copy-paste into a dental PMS.
"""

from __future__ import annotations

import json

from groq import Groq

from app.config import settings
from app.templates import get_template

# ---------------------------------------------------------------------------
# System prompt builders
# ---------------------------------------------------------------------------

def _build_analyze_system(template) -> str:
    note_keys = [key for _, key in template.NOTE_SECTIONS]
    note_json_shape = ",\n    ".join(f'"{k}": "..."' for k in note_keys)

    return f"""\
You are the clarifying agent for a dental scribe application.

You receive the running transcript of a dentist-patient conversation and a
template schema listing every field the note should contain. The transcript
captures BOTH the dentist and the patient speaking during the encounter.

Template: {template.TEMPLATE_NAME}

Your job:
1. Generate a short session title (3-5 words, like "Upper Right Toothache" or
   "Crown Follow-up #14"). This names the session in the sidebar.
2. Extract field values that the transcript already covers.
3. Generate a best-effort {template.TEMPLATE_NAME} note from whatever is
   available. Use dental terminology where the transcript supports it. For
   sections the transcript does not cover, write "Not discussed yet."
4. List the fields still missing.
5. Suggest up to 3 clarifying questions, ordered by clinical priority, that
   would fill the most important gaps. These questions are shown to the
   clinician operating the scribe, so phrase them as prompts for the dentist
   to ask or confirm (e.g., "Ask about duration of symptoms" or "Confirm
   allergy list with patient"). Keep each under 25 words.
6. Based on the symptoms described so far, provide AI-assisted clinical
   suggestions: up to 3 possible differential diagnoses and up to 3
   recommended next steps (examinations, imaging, or treatment options).
   These are decision-support hints for the dentist, NOT definitive diagnoses.

Return STRICT JSON:
{{
  "session_title": "Short Descriptive Title",
  "filled_fields": {{"field_name": "short extracted answer", ...}},
  "missing_fields": ["field_name", ...],
  "note": {{
    {note_json_shape}
  }},
  "clarifying_questions": [
    {{"field": "field_name", "question": "..."}},
    ...
  ],
  "is_complete": true | false,
  "ai_suggestions": {{
    "differential_diagnoses": ["...", "..."],
    "recommended_next_steps": ["...", "..."]
  }}
}}

Rules:
- A field is "filled" only when the transcript clearly answers it. Never invent.
- Set is_complete=true when all required fields are filled.
- IMPORTANT: If is_complete=true, clarifying_questions MUST be an empty array [].
  Only ask questions when there are genuinely missing fields that need input.
- Never ask more than 3 questions at once.
- The note must always be present, even if most sections say "Not discussed yet."
- ai_suggestions must always be grounded in the transcript. Prefix each with
  clinical confidence: "Likely:", "Possible:", or "Consider:" as appropriate.
"""


def _build_final_note_system(template) -> str:
    note_keys = [key for _, key in template.NOTE_SECTIONS]

    return f"""\
You are a dental clinical scribe.

Given the full transcript of a dentist-patient conversation, generate a polished
{template.TEMPLATE_NAME} note. The transcript contains both the dentist and
patient speaking. Return STRICT JSON with EXACTLY these keys:

{", ".join(note_keys)}.

Each value is a concise, professional paragraph grounded ONLY in the transcript.
Use standard dental terminology. If the transcript does not cover a section,
write "Not discussed in this encounter." Never invent clinical findings.
"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def _client() -> Groq:
    if not settings.groq_api_key:
        raise RuntimeError("GROQ_API_KEY is not configured")
    return Groq(api_key=settings.groq_api_key)


def analyze_transcript(transcript: str, template_key: str | None = None) -> dict:
    """Analyze a transcript against the given template.

    Returns a dict matching the ``AnalyzeResponse`` shape (minus session_id
    and rendered_note, which the router adds).
    """
    template = get_template(template_key)
    client = _client()
    field_schema = {k: v["description"] for k, v in template.FIELDS.items()}

    resp = client.chat.completions.create(
        model=settings.llm_model,
        temperature=0.1,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": _build_analyze_system(template)},
            {
                "role": "user",
                "content": json.dumps({
                    "schema": field_schema,
                    "transcript": transcript,
                }),
            },
        ],
    )

    raw = resp.choices[0].message.content or "{}"
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = {}

    note = parsed.get("note", {})
    suggestions = parsed.get("ai_suggestions", {})
    is_complete = bool(parsed.get("is_complete", False))
    questions = parsed.get("clarifying_questions", [])
    if is_complete:
        questions = []
    questions = questions[:3]
    return {
        "session_title": parsed.get("session_title", "Untitled Session"),
        "filled_fields": parsed.get("filled_fields", {}),
        "missing_fields": parsed.get("missing_fields", []),
        "note": note,
        "rendered_note": template.render_note(note),
        "clarifying_questions": questions,
        "is_complete": is_complete,
        "ai_suggestions": {
            "differential_diagnoses": suggestions.get("differential_diagnoses", []),
            "recommended_next_steps": suggestions.get("recommended_next_steps", []),
        },
    }


def generate_final_note(transcript: str, template_key: str | None = None) -> dict:
    """Produce the polished, final-format note."""
    template = get_template(template_key)
    client = _client()

    resp = client.chat.completions.create(
        model=settings.llm_model,
        temperature=0.1,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": _build_final_note_system(template)},
            {"role": "user", "content": transcript},
        ],
    )

    raw = resp.choices[0].message.content or "{}"
    try:
        note = json.loads(raw)
    except json.JSONDecodeError:
        note = {}

    return {"note": note, "rendered_note": template.render_note(note)}
