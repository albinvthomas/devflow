# DevFlow 🚀

DevFlow is an intelligent, automated CI/CD platform that seamlessly connects to your GitHub repositories, analyzes your codebase, and uses AI (Google Gemini) to automatically generate and execute production-ready Docker and GitHub Actions configurations.

## Architecture

```text
+-------------------+       +-----------------------+       +-------------------+
|                   |       |                       |       |                   |
|   React + Vite    | <---> |   FastAPI Backend     | <---> |  PostgreSQL DB    |
|   (Frontend UI)   |       |   (Python 3.11)       |       |                   |
|                   |       |                       |       +-------------------+
+-------------------+       +-----------------------+
        ^                               |
        | (SSE Live Logs)               v
        |                       +-------------------+
        |                       |                   |
        +-----------------------|  Docker Engine    |
                                |  (Local Deploy)   |
                                +-------------------+
```

## Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL
- Docker (must be running on the host machine)

## Quickstart (Docker Compose)

The easiest way to run the entire DevFlow platform is using Docker Compose:

1. Copy `.env.example` to `.env` and fill in your credentials.
2. Run `docker compose up --build`.
3. Open `http://localhost:5173` in your browser.

## Manual Setup

### Backend Setup
1. Create a virtual environment: `python -m venv venv`
2. Activate it: `source venv/bin/activate` (or `venv\Scripts\activate` on Windows)
3. Install dependencies: `pip install -r requirements.txt`
4. Set up your `.env` file (see below).
5. Run the server: `uvicorn main:app --reload`

### Frontend Setup
1. Navigate to the `frontend` directory: `cd frontend`
2. Install dependencies: `npm install`
3. Start the dev server: `npm run dev`

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://user:pass@localhost:5432/devflow_db` |
| `SECRET_KEY` | JWT signing key | `your_secret_key` |
| `GITHUB_CLIENT_ID` | GitHub OAuth App Client ID | `Iv1.abc...` |
| `GITHUB_CLIENT_SECRET`| GitHub OAuth App Secret | `abc...` |
| `GEMINI_API_KEY` | Google Gemini API Key | `AIza...` |
| `VITE_API_URL` | Backend URL for the frontend | `http://localhost:8000` |

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login and receive JWT |
| GET | `/github/connect` | Initiate GitHub OAuth flow |
| POST | `/projects` | Connect a new GitHub repository |
| GET | `/projects` | List user's connected projects |
| POST | `/projects/{id}/generate` | AI generation of DevOps configs |
| POST | `/projects/{id}/deploy` | Trigger a local Docker deployment |
| GET | `/deployments/{id}/stream`| Real-time Server-Sent Events (SSE) logs |

## Screenshots
*(Insert screenshots of the Dashboard, Project Details, and Live Deployment Logs here)*

## Tech Stack
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
