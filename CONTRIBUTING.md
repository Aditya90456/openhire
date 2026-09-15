# Contributing to OpenHire

Thanks for helping improve OpenHire! We prioritize **offline-first local development** and **explainable, evidence-backed code**.

---

## 🛠️ Quick Local Setup

**No external API keys or PostgreSQL required to develop:**

```bash
git clone https://github.com/DevSidd2006/OpenHire.git
cd OpenHire
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                             # Defaults to offline mock mode
python -m uvicorn api.app:app --reload
```

- Server: `http://localhost:8000` | UI: `http://localhost:8000/app` | Docs: `http://localhost:8000/docs`
- Data defaults to in-memory stubs (`repositories/memory.py`). For PostgreSQL, run `docker compose -f docker-compose.postgres.yml up -d` and set `DATABASE_URL`.

---

## 🧪 Testing

OpenHire enforces high test coverage. Always run the test suite before submitting changes:

```bash
pytest tests/ -v
```

The test runner automatically pins providers to `mock` mode to ensure hermetic, zero-cost test execution.

---

## 📐 Core Engineering Conventions

1. **Explain the "Why":** Document non-obvious design rationales and architectural trade-offs in docstrings.
2. **Strict Layer Separation:** Route handlers (`api/routes/`) stay thin; domain logic lives in `services/`; data access goes through `repositories/interfaces.py`.
3. **No Hallucinated Outputs:** LLM outputs must strictly validate against Pydantic schemas in `schemas/llm_outputs.py`. Never invent fallback data for a real candidate.
4. **Protect Candidate Data:** Treat all resumes, interview transcripts, and evaluation outputs as sensitive personal data. Never log PII or commit credentials.

---

## 🚀 Pull Request Workflow

1. Check existing issues or open a new one for proposed feature designs.
2. Create a feature branch: `git checkout -b feat/my-feature` or `fix/my-bug`.
3. Write clean code with corresponding tests in `tests/`.
4. Ensure `pytest tests/ -v` passes completely.
5. Open a Pull Request referencing the issue number.

Please ensure you adhere to our **[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)**. For security vulnerabilities, review **[SECURITY.md](SECURITY.md)**.
