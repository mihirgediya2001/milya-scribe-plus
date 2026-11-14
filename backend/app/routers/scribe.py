"""Scribe routes: transcribe audio, analyze transcript, and finalize notes.

Every endpoint is scoped to the caller's clinic via ``clinic_id``.
"""

import json

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.dependencies import DB, require_permission
from app.models import AuditLog, ScribeSession, SessionStatus, User, UserRole
from app.schemas.scribe import (
    AISuggestions,
    AnalyzeRequest,
    AnalyzeResponse,
    ClarifyingQuestion,
    FinalizeRequest,
    FinalizeResponse,
    SessionDetail,
    SessionOut,
    TemplateField,
    TemplateInfo,
    TranscribeResponse,
)
from app.services.agent import analyze_transcript, generate_final_note
from app.services.transcription import transcribe_audio
from app.templates import DEFAULT_TEMPLATE_KEY, TEMPLATE_LIST, get_template

router = APIRouter(prefix="/api/scribe", tags=["scribe"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_template_fields(template, filled: dict, missing: list) -> list[TemplateField]:
    """Merge filled/missing info with the template metadata."""
    fields: list[TemplateField] = []
    for key, meta in template.FIELDS.items():
        if key in filled:
            fields.append(TemplateField(
                name=key, label=meta["label"], value=filled[key], status="filled",
            ))
        else:
            fields.append(TemplateField(
                name=key, label=meta["label"], value="", status="missing",
            ))
    return fields


def _audit(db, user, action: str, target_type: str = "", target_id: str = "", details: str = ""):
    db.add(AuditLog(
        clinic_id=user.clinic_id,
        user_id=user.id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        details=details,
    ))
    db.commit()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/templates", response_model=list[TemplateInfo])
def list_templates():
    """Return all available summary templates."""
    return [TemplateInfo(**t) for t in TEMPLATE_LIST]


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(
    audio: UploadFile = File(...),
    user=require_permission("record"),
    db: DB = None,  # type: ignore[assignment]
):
    """Convert an audio recording to text via Whisper."""
    data = await audio.read()
    if not data:
        raise HTTPException(400, "Empty audio file")

    try:
        text = transcribe_audio(data, audio.filename or "audio.webm")
    except RuntimeError as exc:
        raise HTTPException(503, str(exc))

    _audit(db, user, "transcribe", details=f"length={len(data)}")
    return TranscribeResponse(text=text)


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(
    req: AnalyzeRequest,
    user=require_permission("record"),
    db: DB = None,  # type: ignore[assignment]
):
    """Analyze the transcript: fill the template, flag gaps, suggest questions."""
    if not req.transcript.strip():
        raise HTTPException(400, "Transcript is empty")

    template_key = req.template_key or DEFAULT_TEMPLATE_KEY

    try:
        result = analyze_transcript(req.transcript, template_key=template_key)
    except RuntimeError as exc:
        raise HTTPException(503, str(exc))

    template = get_template(template_key)
    suggestions = result.get("ai_suggestions", {})

    if req.session_id:
        session = (
            db.query(ScribeSession)
            .filter(
                ScribeSession.id == req.session_id,
                ScribeSession.clinic_id == user.clinic_id,
            )
            .first()
        )
        if session is None:
            raise HTTPException(404, "Session not found")
        session.transcript = req.transcript
        session.template_key = template_key
        session.note_json = json.dumps(result["note"])
        session.note_rendered = result["rendered_note"]
        session.suggestions_json = json.dumps(suggestions)
        if not session.title:
            session.title = result.get("session_title", "Untitled Session")
    else:
        session = ScribeSession(
            clinic_id=user.clinic_id,
            user_id=user.id,
            title=result.get("session_title", "Untitled Session"),
            template_key=template_key,
            transcript=req.transcript,
            note_json=json.dumps(result["note"]),
            note_rendered=result["rendered_note"],
            suggestions_json=json.dumps(suggestions),
        )
        db.add(session)

    db.commit()
    db.refresh(session)

    _audit(db, user, "analyze", "session", session.id)

    return AnalyzeResponse(
        session_id=session.id,
        session_title=session.title or "Untitled Session",
        note=result["note"],
        rendered_note=result["rendered_note"],
        template_fields=_build_template_fields(
            template, result["filled_fields"], result["missing_fields"],
        ),
        clarifying_questions=[
            ClarifyingQuestion(**q) for q in result["clarifying_questions"]
        ],
        is_complete=result["is_complete"],
        ai_suggestions=AISuggestions(**suggestions),
    )


@router.post("/finalize", response_model=FinalizeResponse)
def finalize(
    req: FinalizeRequest,
    user=require_permission("finalize"),
    db: DB = None,  # type: ignore[assignment]
):
    """Generate the polished final note and mark the session as finalized."""
    session = (
        db.query(ScribeSession)
        .filter(
            ScribeSession.id == req.session_id,
            ScribeSession.clinic_id == user.clinic_id,
        )
        .first()
    )
    if session is None:
        raise HTTPException(404, "Session not found")

    try:
        result = generate_final_note(session.transcript, template_key=session.template_key)
    except RuntimeError as exc:
        raise HTTPException(503, str(exc))

    session.note_json = json.dumps(result["note"])
    session.note_rendered = result["rendered_note"]
    session.status = SessionStatus.FINALIZED
    db.commit()

    _audit(db, user, "finalize", "session", session.id)

    return FinalizeResponse(
        session_id=session.id,
        note=result["note"],
        rendered_note=result["rendered_note"],
    )


@router.get("/sessions/{session_id}", response_model=SessionDetail)
def get_session(
    session_id: str,
    user=require_permission("record"),
    db: DB = None,  # type: ignore[assignment]
):
    """Return a single session with full transcript for resume."""
    session = (
        db.query(ScribeSession)
        .filter(
            ScribeSession.id == session_id,
            ScribeSession.clinic_id == user.clinic_id,
        )
        .first()
    )
    if session is None:
        raise HTTPException(404, "Session not found")

    if user.role == UserRole.ASSISTANT and session.user_id != user.id:
        raise HTTPException(403, "You can only access your own sessions")
    if user.role == UserRole.DENTIST:
        owner = db.query(User).filter(User.id == session.user_id).first()
        if session.user_id != user.id and (not owner or owner.role != UserRole.ASSISTANT):
            raise HTTPException(403, "You can only access your own or assistant sessions")

    return SessionDetail(
        id=session.id,
        title=session.title or "Untitled Session",
        template_key=session.template_key or DEFAULT_TEMPLATE_KEY,
        transcript=session.transcript,
        note_rendered=session.note_rendered or "",
        status=session.status.value,
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
    )


@router.get("/sessions", response_model=list[SessionOut])
def list_sessions(
    user=require_permission("record"),
    db: DB = None,  # type: ignore[assignment]
):
    """List scribe sessions filtered by role.

    Admin: all clinic sessions.  Dentist: own + assistant sessions.
    Assistant: own sessions only.
    """
    query = db.query(ScribeSession).filter(
        ScribeSession.clinic_id == user.clinic_id,
    )

    if user.role == UserRole.DENTIST:
        assistant_ids = [
            u.id for u in db.query(User).filter(
                User.clinic_id == user.clinic_id,
                User.role == UserRole.ASSISTANT,
            ).all()
        ]
        allowed_ids = [user.id] + assistant_ids
        query = query.filter(ScribeSession.user_id.in_(allowed_ids))
    elif user.role == UserRole.ASSISTANT:
        query = query.filter(ScribeSession.user_id == user.id)

    rows = query.order_by(ScribeSession.updated_at.desc()).limit(50).all()

    user_cache: dict[str, str] = {}
    def get_name(uid: str) -> str:
        if uid not in user_cache:
            u = db.query(User).filter(User.id == uid).first()
            user_cache[uid] = u.name if u else "Unknown"
        return user_cache[uid]

    return [
        SessionOut(
            id=r.id,
            title=r.title or "Untitled Session",
            status=r.status.value,
            created_by=get_name(r.user_id),
            created_at=r.created_at.isoformat(),
            updated_at=r.updated_at.isoformat(),
        )
        for r in rows
    ]
