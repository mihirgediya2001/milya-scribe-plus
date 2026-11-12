"""Speech-to-text via Groq's Whisper API (free tier).

A dental-specific initial prompt biases the model toward clinical vocabulary.
"""

import os
import tempfile
from pathlib import Path

from groq import Groq

from app.config import settings

DENTAL_PROMPT = (
    "Dental clinical conversation. Terms: caries, occlusal, buccal, lingual, "
    "mesial, distal, periodontal, periapical, endodontic, composite, amalgam, "
    "crown, bridge, implant, extraction, scaling, root planing, gingivitis, "
    "abscess, pulpitis, radiograph, bitewing, panoramic."
)


def _client() -> Groq:
    if not settings.groq_api_key:
        raise RuntimeError("GROQ_API_KEY is not configured")
    return Groq(api_key=settings.groq_api_key)


def transcribe_audio(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    """Send an audio blob to Whisper and return the transcript text."""
    client = _client()
    suffix = Path(filename).suffix or ".webm"

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as fh:
            result = client.audio.transcriptions.create(
                model=settings.stt_model,
                file=fh,
                response_format="text",
                prompt=DENTAL_PROMPT,
            )
        text = result if isinstance(result, str) else getattr(result, "text", "")
        return text.strip()
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
