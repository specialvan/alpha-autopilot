# backend

FastAPI backend for the alpha-autopilot narrative recommendation prototype.

## Structure

- `app/main.py` - FastAPI app entrypoint
- `app/core/config.py` - application settings
- `app/api/routes/` - HTTP routes
- `app/services/narrative/` - dashboard, preview, training, feedback, and schema services

## Run

```bash
uvicorn backend.app.main:app --reload
```

## Endpoints

- `GET /api/dashboard`
- `POST /api/recommendation/preview`
- `POST /api/training`
- `POST /api/feedback`
