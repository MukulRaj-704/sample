# Dynamic AI Interview Module (Django)

This repository now includes a runnable Django project with an `interviews` app for adaptive AI-style interviews.

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Features
- Parses resume text and extracts skill keywords.
- Generates **at least 25 initial questions** from resume keywords.
- Runs interview one question at a time.
- Adapts by adding follow-up questions based on candidate answer keywords.
- Supports `text` and `voice` modes (`voice` expects transcribed text in `answer_text`).
- Evaluates answers with simple rubric scoring and mistake analysis.
- Produces final interview summary and improvement suggestions.

## API Endpoints
Project routes already include `interviews.urls` in `config/urls.py`.

Endpoints:
- `POST /interviews/start/`
- `POST /interviews/answer/`
- `GET /interviews/report/<session_id>/`

## Running tests
```bash
python manage.py test interviews
```

## Notes
- This implementation uses deterministic NLP heuristics (no external LLM required).
- For production voice interviews, integrate speech-to-text before calling `/interviews/answer/`.
