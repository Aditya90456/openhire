# OpenHire — Product Context

**OpenHire** is an AI-powered platform for high-volume candidate screening, using structured voice interviews and a multi-agent evaluation pipeline.

---

## 🎯 Core Flow

1. **Job Requisition:** Recruiter creates a job posting and configures competency rubrics.
2. **Resume Matching:** Candidate applies with a resume (.pdf/.docx); the system matches against the rubric using grounded evidence.
3. **Adaptive Voice Interview:** Shortlisted candidates complete an on-demand voice interview with adaptive follow-ups.
4. **Multi-Agent Evaluation:** Sealed transcripts are scored across 13 specialized LLM agents (Technical, Behavioral, Integrity, Bias, etc.).
5. **Leaderboard & Reporting:** Recruiter views explainable, evidence-backed candidate reports and rankings.

---

## 🛠️ Tech Stack

| Layer | Technology |
|:---|:---|
| **Backend** | Python 3.13, FastAPI, Uvicorn |
| **Agents & AI** | LangGraph, Pydantic v2 |
| **LLMs** | NVIDIA NIM, Groq, OpenAI, Google Gemini, Mock Provider |
| **Voice / Speech** | Edge-TTS, Azure Speech SDK, WebSockets |
| **Persistence** | PostgreSQL 13+ (`asyncpg`), In-Memory stubs |
| **Frontend** | Vanilla HTML5, CSS3, ES6 JavaScript (served at `/app`) |
| **Auth & Security** | JWT (access & refresh tokens), bcrypt, Fernet encryption (BYOK) |

---

## 👥 Target Audience

Hiring teams and university campus recruiters screening large candidate pools who need fast, fair, and evidence-backed evaluation without manual preliminary phone calls.
