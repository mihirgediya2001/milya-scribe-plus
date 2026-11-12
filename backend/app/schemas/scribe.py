"""Request and response schemas for the scribe feature."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class TranscribeResponse(BaseModel):
    text: str


class AnalyzeRequest(BaseModel):
    """Sent on every turn: the full running transcript so far."""

    transcript: str
    session_id: Optional[str] = None  # omit on the first call


class TemplateField(BaseModel):
    name: str
    label: str
    value: str
    status: str  # "filled" | "missing"


class ClarifyingQuestion(BaseModel):
    field: str
    question: str


class AISuggestions(BaseModel):
    differential_diagnoses: list[str] = []
    recommended_next_steps: list[str] = []


class AnalyzeResponse(BaseModel):
    session_id: str
    session_title: str = "Untitled Session"
    note: dict[str, str]
    rendered_note: str
    template_fields: list[TemplateField]
    clarifying_questions: list[ClarifyingQuestion]
    is_complete: bool
    ai_suggestions: AISuggestions = AISuggestions()


class FinalizeRequest(BaseModel):
    session_id: str


class FinalizeResponse(BaseModel):
    session_id: str
    note: dict[str, str]
    rendered_note: str


class SessionOut(BaseModel):
    id: str
    title: str = "Untitled Session"
    status: str
    created_by: str = ""
    created_at: str
    updated_at: str


class SessionDetail(BaseModel):
    id: str
    title: str = "Untitled Session"
    transcript: str
    note_rendered: str
    status: str
    created_at: str
    updated_at: str
