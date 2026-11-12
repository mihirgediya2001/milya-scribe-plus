# Milya Scribe Plus

AI-powered dental clinical documentation with intelligent clarifying questions.

## Features

- **Voice + Text input**: Record patient conversations or type them in. Whisper with dental vocabulary bias handles transcription.
- **Smart Clarifying Agent**: The LLM analyzes the transcript against a Comprehensive Examination template, generates a note AND identifies missing fields with one-at-a-time follow-up questions.
- **AI Clinical Suggestions**: Differential diagnoses and recommended next steps grounded in the transcript (dentist/admin only).
- **Structured Notes**: Outputs a formatted clinical note ready to paste into any dental PMS.
- **Multi-Tenancy**: Each clinic's data is fully isolated via `clinic_id` on every table.
- **RBAC**: Three roles (Admin, Dentist, Assistant) with distinct dashboards and permissions.
- **Session Access Control**: Admin sees all sessions, Dentist sees own + assistant's, Assistant sees own only.
- **Session Auto-naming**: LLM generates concise 3-5 word session titles during analysis.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI, SQLAlchemy, SQLite |
| Frontend | Vanilla HTML/CSS/JS (no build step) |
| STT | Groq Whisper large-v3-turbo |
| LLM | Groq Qwen 27B |
| Auth | bcrypt password hashing, Bearer token sessions |

## Local Development

```bash
cd backend
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

Create `backend/.env`:
```
GROQ_API_KEY=your_key_here
```

Run:
```bash
cd backend
uvicorn app.main:app --reload
```

Open http://localhost:8000

## Deploy to Render

1. Push to GitHub
2. Connect repo on [Render](https://render.com)
3. Set `GROQ_API_KEY` environment variable
4. Deploy (uses `render.yaml` blueprint)
