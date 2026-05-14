# NextGen DM — Instagram Automation Platform

Automate Instagram DMs, comment replies, and follow-to-unlock flows using Meta's official APIs.

---

## Local Development Setup

### Prerequisites
- Python 3.12
- Bun (install from bun.sh)
- Docker Desktop (only used for Redis — one command)

---

## Step 1 — Start Redis

Redis runs as a single Docker container. No setup needed.

```bash
docker run -d -p 6379:6379 --name redis redis
```

To stop it later: `docker stop redis`

---

## Step 2 — Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy env file and fill in values
copy .env.example .env
# (Your .env in the root is already filled — copy values from there)
```

Create a `.env` file inside the `backend/` folder with these values:

```
SUPABASE_DB_URL=postgresql://postgres.<your-project-ref>:<password>@db.<your-project-ref>.supabase.co:5432/postgres
SUPABASE_URL=https://<your-project-ref>.supabase.co
SUPABASE_ANON_KEY=<your-supabase-anon-key>
SUPABASE_SERVICE_ROLE_KEY=<your-supabase-service-role-key>
JWT_SECRET=<generate-with: openssl rand -base64 64>
META_APP_ID=<your-meta-app-id>
META_APP_SECRET=<your-meta-app-secret>
META_VERIFY_TOKEN=<choose-a-random-string>
REDIS_URL=redis://localhost:6379
INSTAGRAM_REDIRECT_URI=http://localhost:8000/api/v1/instagram/callback
FRONTEND_URL=http://localhost:3000
ALLOWED_ORIGINS=["http://localhost:3000"]
DEBUG=true
```

### Run database migrations

```bash
cd backend
alembic upgrade head
```

### Start backend API

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Backend runs at: http://localhost:8000
API docs (dev mode): http://localhost:8000/docs

### Start Celery worker (separate terminal)

```bash
cd backend
celery -A app.workers.celery_app worker --loglevel=info -Q dm_queue,webhook_queue,maintenance
```

---

## Step 3 — Frontend Setup

```bash
cd frontend

# Install dependencies
bun install

# Start dev server
bun run dev
```

Frontend runs at: http://localhost:3000

---

## Step 4 — Webhook Setup (for Instagram automation to work)

Meta requires a public HTTPS URL to send webhook events (comments, DMs).

Install and run ngrok:

```bash
# Install ngrok from ngrok.com
ngrok http 8000
```

You will get a URL like `https://abc123.ngrok.io`.

Then:
1. Go to Meta Developer Dashboard → Your App → Webhooks
2. Set Callback URL: `https://abc123.ngrok.io/api/v1/webhooks/meta`
3. Set Verify Token: `NextGenDMWebhook2026`
4. Subscribe to: `instagram_comments`, `messages`

Also update in `backend/.env`:
```
INSTAGRAM_REDIRECT_URI=https://abc123.ngrok.io/api/v1/instagram/callback
```

---

## Project Structure

```
NextGenDM/
├── backend/
│   ├── app/
│   │   ├── api/v1/        # Route handlers
│   │   ├── core/          # Config, security, dependencies
│   │   ├── database/      # SQLAlchemy setup
│   │   ├── models/        # Database models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   ├── workers/       # Celery tasks
│   │   └── main.py        # FastAPI app
│   ├── alembic/           # Database migrations
│   └── requirements.txt
└── frontend/
    ├── app/               # Next.js pages
    ├── components/        # UI components
    ├── services/          # API calls
    ├── store/             # Zustand state
    ├── types/             # TypeScript types
    └── hooks/
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/auth/signup | Register |
| POST | /api/v1/auth/login | Login |
| GET | /api/v1/instagram/connect | Get OAuth URL |
| GET | /api/v1/instagram/callback | OAuth callback |
| GET | /api/v1/automations/ | List automations |
| POST | /api/v1/automations/ | Create automation |
| PATCH | /api/v1/automations/{id}/toggle | Enable/disable |
| GET | /api/v1/webhooks/meta | Webhook verify |
| POST | /api/v1/webhooks/meta | Webhook events |
| GET | /api/v1/logs/ | Activity logs |
| GET | /api/v1/dashboard/stats | Dashboard stats |
