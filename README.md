# AURIXA

## Autonomous Enterprise AI Platform

AURIXA is an Autonomous Enterprise AI Platform designed to process enterprise requests using multi-agent AI orchestration, workflow automation, Retrieval-Augmented Generation (RAG), policy validation, human approval, document processing, monitoring, and audit logging.

---

## Features

- Multi-agent AI orchestration
- Request classification
- Automation decision engine
- Document and invoice processing
- Invoice policy validation
- RAG-based knowledge retrieval
- Workflow execution engine
- Human-in-the-loop approval system
- Tool execution with retry support
- Prompt security validation
- Email notifications using Brevo
- Authentication and authorization
- Audit logging
- Monitoring dashboard APIs
- Document upload and processing
- Workflow retry support
- AI result validation and evaluation

---

## Architecture

AURIXA follows a layered architecture:

```text
React Frontend
       |
       v
FastAPI Backend
       |
       +-------------------+
       |                   |
       v                   v
AI Orchestrator      Workflow Engine
       |                   |
       v                   v
AI Agents           Human Approval
       |
       +---------+---------+
       |         |         |
       v         v         v
      RAG      Tools    Policies
       |
       v
   ChromaDB

       |
       v
 SQLite Database
```

Detailed architecture diagrams are available in:

```text
docs/architecture_diagrams.md
```

---

## Technology Stack

### Frontend

- React
- Vite
- JavaScript
- CSS

### Backend

- Python
- FastAPI
- Uvicorn
- SQLAlchemy Async
- Pydantic

### Database

- SQLite
- Aiosqlite

### AI and RAG

- Multi-Agent Architecture
- ChromaDB
- PDF Processing
- Retrieval-Augmented Generation

### External Services

- Brevo Email API

### Testing

- Pytest
- Pytest Asyncio
- Pytest Coverage

---

# Project Structure

```text
AURIXA/
│
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   ├── analytics/
│   │   ├── api/
│   │   ├── core/
│   │   ├── documents/
│   │   ├── models/
│   │   ├── monitoring/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── workflows/
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── docs/
│   └── architecture_diagrams.md
│
├── prompts/
├── tests/
└── workflows/
```

---

# Installation

## 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd AURIXA
```

---

## 2. Backend Setup

Navigate to the backend folder:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Environment Configuration

Create a `.env` file inside the `backend` folder.

Example:

```env
ENVIRONMENT=development
DEBUG=true

DATABASE_URL=sqlite+aiosqlite:///./aurixa.db

SECRET_KEY=your-secret-key

FRONTEND_URL=http://localhost:5173

BREVO_API_KEY=your-brevo-api-key
BREVO_SENDER_EMAIL=your-verified-email@example.com
```

Do not upload your real API keys to GitHub.

---

# Run the Backend

From the `backend` directory:

```bash
uvicorn app.main:app --reload
```

The backend will run at:

```text
http://127.0.0.1:8000
```

---

# API Documentation

FastAPI automatically provides interactive API documentation.

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

# Main API Modules

The platform provides APIs for:

- Authentication
- Requests
- AI Agents
- Workflows
- Workflow Executions
- Human Approvals
- Tools
- Documents
- Audit Logs
- Monitoring

Example API prefix:

```text
/api/v1
```

Example endpoints:

```text
POST /api/v1/auth/register
POST /api/v1/auth/login

POST /api/v1/requests
GET  /api/v1/requests

POST /api/v1/agents/orchestrate

POST /api/v1/workflows/{workflow_name}/execute
GET  /api/v1/workflows/executions

GET  /api/v1/approvals
PATCH /api/v1/approvals/{approval_id}

POST /api/v1/documents/ingest

GET /api/v1/monitoring/summary
```

---

# AI Workflow

AURIXA processes requests through the following pipeline:

```text
User Request
     |
     v
Prompt Validation
     |
     v
Classifier Agent
     |
     v
Automation Agent
     |
     +-----------------------+
     |                       |
     v                       v
Document Processing       RAG Research
     |                       |
     +-----------+-----------+
                 |
                 v
           Policy Validation
                 |
                 v
           Tool Execution
                 |
                 v
          Validation Agent
                 |
                 v
       Human Approval Required?
             /        \
           Yes         No
            |           |
            v           v
        Approval     Complete
```

---

# Human Approval

AURIXA supports Human-in-the-Loop workflows.

When an AI result requires approval:

1. The workflow is paused.
2. An approval record is created.
3. The workflow status becomes `waiting_approval`.
4. A human reviewer approves or rejects the request.
5. The workflow continues or stops based on the decision.

---

# RAG Pipeline

The RAG system processes knowledge as follows:

```text
Document
   |
   v
Text Extraction
   |
   v
Chunking
   |
   v
Embedding
   |
   v
ChromaDB
   |
   v
Similarity Retrieval
   |
   v
Research Agent
   |
   v
AI Response
```

---

# Email Notifications

AURIXA supports email notifications through Brevo.

The notification service can send:

- Workflow notifications
- Approval notifications
- Automation results
- System alerts

Configuration requires:

```env
BREVO_API_KEY=your-api-key
BREVO_SENDER_EMAIL=your-email
```

---

# Testing

Navigate to the backend directory:

```bash
cd backend
```

Run all tests:

```bash
pytest
```

Run tests with detailed output:

```bash
pytest -v
```

Run tests with coverage:

```bash
pytest --cov=app
```

---

# Monitoring

The monitoring API provides system-level information about:

- Total requests
- Pending requests
- Completed requests
- Failed requests
- Workflow executions
- Running workflows
- Workflows waiting for approval
- Approval statistics

Endpoint:

```text
GET /api/v1/monitoring/summary
```

---

# Security

AURIXA includes:

- Authentication
- Protected API endpoints
- Prompt validation
- Input validation
- Policy validation
- Human approval controls
- Audit logging

---

# Deployment

The application can be deployed with:

- Render
- Railway
- Fly.io
- Docker-compatible cloud platforms

The frontend can be deployed separately using:

- Vercel
- Netlify

Update the production environment variables before deployment.

---

# Version

Current Version:

```text
0.1.0
```

---

# License

This project was developed as an Autonomous Enterprise AI Platform implementation.

---

## AURIXA

**Autonomous Enterprise AI Platform — Intelligent Agents, Workflows, RAG, Human Approval, and Enterprise Automation.**