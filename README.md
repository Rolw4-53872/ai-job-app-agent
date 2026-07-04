# AI Job Application Agent

A production-ready **AI Job Application Agent** designed to automate job searches, company research, resume parsing, custom email generation, inbox response analysis, and WhatsApp alerts while keeping the **human (you) in control** of all outbound communication.

## Key Features

1. **Profile Management & Resume Parser**: Upload a PDF resume to extract skills, experience, projects, and programming languages automatically using OpenAI GPT models, syncing details directly to the dashboard profile.
2. **Company Research Agent**: Input a company name or website, and the agent gathers descriptions, industry, tech stacks, public hiring contact formats, and HR profiles.
3. **Personalized Email Writer**: Generates custom, non-generic application letters for each company based on your CV profile + company profile + position description. Allows real-time tonal updates (Professional, Bold, Warm, Concise, Technical).
4. **Human-in-the-Loop Guardrail**: A strict database state gate blocks email dispatch until you review, edit/regenerate, and click "Approve & Send" on the dashboard.
5. **Inbox Reply Analyzer & WhatsApp Alerts**: Classifies recruiter replies (e.g. Interview invitation, Assessment, Rejection) using AI, extracts priority levels, drafts suggested responses, and sends critical updates instantly via WhatsApp Cloud API.
6. **AI Assistant Chatbot**: Integrated floating assistant widget to query job search statistics (e.g., "how many interview invitations do I have?", "who hasn't replied?") and trigger automated routing actions.

---

## Technology Stack

* **Backend**: FastAPI, Python 3.10, PostgreSQL, SQLAlchemy ORM, Alembic migrations, python-jose (JWT Auth), PyPDF (text extraction).
* **Frontend**: Vite, React, Vanilla CSS, Recharts (visualizations), Lucide React (sleek icons).
* **Automation**: n8n workflows.
* **Orchestration**: Docker, Docker Compose.

---

## Folder Structure

```
ai_job_app_agent/
├── backend/
│   ├── app/
│   │   ├── api/            # API routers (auth, profile, applications, email, etc.)
│   │   ├── core/           # Config settings, DB connections, JWT security
│   │   ├── models/         # SQLAlchemy DB models (User, Profile, application, email)
│   │   ├── schemas/        # Pydantic schemas (request/response validation)
│   │   ├── services/       # AI, Gmail API, WhatsApp Cloud API integrations
│   │   └── main.py         # Entry point
│   ├── alembic/            # Migrations configuration
│   ├── tests/              # Pytest isolation database test suite
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── services/       # API wrapper client (localstorage JWT attachment)
│   │   ├── App.jsx         # Layout views, stats charts, float chatbot
│   │   ├── index.css       # Core styling & dark mode tokens
│   │   └── main.jsx
│   ├── index.html
│   ├── Dockerfile
│   └── package.json
├── n8n/
│   ├── workflow_outbound.json
│   ├── workflow_inbound.json
│   └── README.md
├── docker-compose.yml
└── README.md
```

---

## Getting Started

### Prerequisites

* Docker and Docker Compose installed.
* OpenAI API key (for production LLM support).
* Google OAuth credentials (for production Gmail sync).
* Meta WhatsApp Business Phone Number ID & Access Token (for WhatsApp notifications).

### Run Locally (Docker Compose)

1. Clone or set this folder as your active workspace directory:
   `C:\Users\RolaA\.gemini\antigravity\scratch\ai_job_app_agent`

2. Build and launch all services:
   ```bash
   docker-compose up --build
   ```

3. The system will download images, spin up PostgreSQL, seed databases, and map the following ports:
   * **Frontend Web Dashboard**: `http://localhost:3000`
   * **FastAPI Backend (Swagger API Docs)**: `http://localhost:8000/docs`
   * **PostgreSQL Database**: `localhost:5432`

---

## Development & Sandbox Testing

### 1. Mock Mode (Sandbox)
By default, the backend runs with `MOCK_MODE=True` (configured in `docker-compose.yml` or `.env`). In this state:
* Resume parsing, company research, email writing, and chatbot responses simulate OpenAI GPT completions using high-quality templates if `OPENAI_API_KEY` is not active.
* Email sending simulates a Gmail dispatch, printing details directly to logs without requiring Google credentials.
* WhatsApp notifications print rich cards in logs.
* *This allows the entire system to be tested locally in under 2 minutes.*

### 2. Switching to Production APIs
To connect real endpoints, configure variables in a `.env` file in the `backend/` directory:
```env
MOCK_MODE=False
OPENAI_API_KEY=your_openai_key
GMAIL_CLIENT_ID=your_google_id
GMAIL_CLIENT_SECRET=your_google_secret
WHATSAPP_ACCESS_TOKEN=your_whatsapp_token
WHATSAPP_PHONE_NUMBER_ID=your_whatsapp_phone_id
```

### Running Tests
To run backend unit tests covering JWT authentication, database schemas, and AI application flows:
1. Enter the backend directory and execute:
   ```bash
   pytest
   ```
   *Note: Tests run using an isolated, in-memory SQLite database (`tests/conftest.py`), meaning they will not modify or interfere with your active PostgreSQL records.*
