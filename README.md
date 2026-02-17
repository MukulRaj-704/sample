# Dynamic AI Interview Module (Django)

This repository now includes an `interviews` Django app for adaptive AI-style interviews.

## Features
- Parses resume text and extracts skill keywords.
- Generates **at least 25 initial questions** from resume keywords.
- Runs interview one question at a time.
- Adapts by adding follow-up questions based on candidate answer keywords.
- Supports `text` and `voice` modes (`voice` expects transcribed text in `answer_text`).
- Evaluates answers with simple rubric scoring and mistake analysis.
- Produces final interview summary and improvement suggestions.

## API Endpoints
Add `interviews.urls` in your project `urls.py`:

```python
path("interviews/", include("interviews.urls"))
```

Endpoints:
- `POST /interviews/start/`
- `POST /interviews/answer/`
- `GET /interviews/report/<session_id>/`

## Notes
- This implementation uses deterministic NLP heuristics (no external LLM required).
- For production voice interviews, integrate speech-to-text before calling `/answer/`.
