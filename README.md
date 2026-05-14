# DevFlow 🚀

**Live Application:** [https://devflow-psi-seven.vercel.app](https://devflow-psi-seven.vercel.app)

DevFlow is an intelligent, automated CI/CD platform that seamlessly connects to your GitHub repositories, analyzes your codebase, and uses AI (Google Gemini) to automatically generate and execute production-ready Docker and GitHub Actions configurations.

## What it does

- **GitHub Integration:** securely connect your GitHub account via OAuth to browse and select your repositories.
- **AI-Powered Codebase Analysis:** utilizes Google Gemini to scan your project's technology stack and recommend the perfect Dockerfile, `docker-compose.yml`, and CI/CD pipelines.
- **Automated Container Deployments:** trigger remote simulated or local Docker builds with a single click.
- **Real-time Streaming Logs:** watch the live terminal output of your deployment progress via Server-Sent Events (SSE).
- **Secure Authentication:** full JWT-based authentication system with encrypted PostgreSQL storage.

## The Tech Stack

![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)

**Frontend:**
- React (Vite)
- TailwindCSS
- React Router
- Lucide Icons
- Server-Sent Events (SSE) Client

**Backend:**
- FastAPI (Python 3.11)
- Google Gemini AI API
- PostgreSQL (via neon.tech)
- SQLAlchemy (Async ORM) & Pydantic
- psycopg Database Driver
- GitHub OAuth Integration

## Architecture Overview

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
        +-----------------------|  Docker Engine /  |
                                |  Simulation Mode  |
                                +-------------------+
```
