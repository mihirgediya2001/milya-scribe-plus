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
from app.templates.comprehensive_exam import FIELDS, render_note

# ---------------------------------------------------------------------------
# System prompts
# ---------------------------------------------------------------------------

ANALYZE_SYSTEM = """\
You are the clarifying agent for a dental scribe application.

You receive the running transcript of a dentist-patient conversation and a
template schema listing every field the note should contain.

Your job:
1. Generate a short session title (3-5 words, like "Upper Right Toothache" or
   "Crown Follow-up #14"). This names the session in the sidebar.
2. Extract field values that the transcript already covers.
3. Generate a best-effort Comprehensive Examination note from whatever is
   available. Use dental terminology where the transcript supports it. For
   sections the transcript does not cover, write "Not discussed yet."
4. List the fields still missing.
5. Suggest up to 3 clarifying questions, ordered by clinical priority, that
   would fill the most important gaps. Write each question in warm, plain
   language a dentist would use with a patient. Keep each under 25 words.
6. Based on the symptoms described so far, provide AI-assisted clinical
   suggestions: up to 3 possible differential diagnoses and up to 3
   recommended next steps (examinations, imaging, or treatment options).
   These are decision-support hints for the dentist, NOT definitive diagnoses.

Return STRICT JSON:
{
  "session_title": "Short Descriptive Title",
  "filled_fields": {"field_name": "short extracted answer", ...},
  "missing_fields": ["field_name", ...],
  "note": {
    "chief_complaint": "...",
    "pain_history": "...",
    "medical_history": "...",
    "oral_hygiene": "...",
    "diet_habits": "...",
    "previous_treatment": "...",
    "clinical_examination": "...",
    "diagnosis": "...",
    "treatment_plan": "...",
    "next_appointment": "..."
  },
  "clarifying_questions": [
    {"field": "field_name", "question": "..."},
    ...
  ],
  "is_complete": true | false,
  "ai_suggestions": {
    "differential_diagnoses": ["...", "..."],
    "recommended_next_steps": ["...", "..."]
  }
}

Rules:
- A field is "filled" only when the transcript clearly answers it. Never invent.
- Set is_complete=true when all required fields are filled.
- IMPORTANT: If is_complete=true, clarifying_questions MUST be an empty array [].
  Only ask questions when there are genuinely missing fields that need patient input.
- Never ask more than 3 questions at once.
- The note must always be present, even if most sections say "Not discussed yet."
- ai_suggestions must always be grounded in the transcript. Prefix each with
  clinical confidence: "Likely:", "Possible:", or "Consider:" as appropriate.
"""

FINAL_NOTE_SYSTEM = """\
You are a dental clinical scribe.

Given the full transcript of a dentist-patient conversation, generate a polished
Comprehensive Examination note. Return STRICT JSON with EXACTLY these keys:

chief_complaint, pain_history, medical_history, oral_hygiene, diet_habits,
previous_treatment, clinical_examination, diagnosis, treatment_plan,
next_appointment.

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


def analyze_transcript(transcript: str) -> dict:
    """Analyze a transcript against the Comprehensive Exam template.

    Returns a dict matching the ``AnalyzeResponse`` shape (minus session_id
    and rendered_note, which the router adds).
    """
    client = _client()
    field_schema = {k: v["description"] for k, v in FIELDS.items()}

    resp = client.chat.completions.create(
        model=settings.llm_model,
        temperature=0.1,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": ANALYZE_SYSTEM},
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
        "rendered_note": render_note(note),
        "clarifying_questions": questions,
        "is_complete": is_complete,
        "ai_suggestions": {
            "differential_diagnoses": suggestions.get("differential_diagnoses", []),
            "recommended_next_steps": suggestions.get("recommended_next_steps", []),
        },
    }


def generate_final_note(transcript: str) -> dict:
    """Produce the polished, final-format note."""
    client = _client()

    resp = client.chat.completions.create(
        model=settings.llm_model,
        temperature=0.1,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": FINAL_NOTE_SYSTEM},
            {"role": "user", "content": transcript},
        ],
    )

    raw = resp.choices[0].message.content or "{}"
    try:
        note = json.loads(raw)
    except json.JSONDecodeError:
        note = {}

    return {"note": note, "rendered_note": render_note(note)}
