# Security Policy

OpenHire processes resumes, transcripts, and evaluation data. We take candidate privacy and security seriously.

---

## 🔒 Reporting a Vulnerability

**Please do not report security issues via public GitHub issues.**

Use one of the following private reporting channels:
1. **GitHub Private Vulnerability Reporting:** Click **"Report a vulnerability"** under this repository's **Security** tab (recommended).
2. **Email Maintainer:** Send details to [kushwahasiddhartha31@gmail.com](mailto:kushwahasiddhartha31@gmail.com) with subject `OpenHire Security`.

Please provide reproduction steps, an assessment of potential impact, and the commit/branch tested. We aim to acknowledge reports within 72 hours.

---

## 🎯 Vulnerability Scope

Key vulnerabilities we prioritize:
* Unauthorized access to another user's resumes, transcripts, or evaluations.
* Privilege escalation (e.g. candidate $\rightarrow$ recruiter / admin).
* Credential or API key leakage in logs, error payloads, or responses.
* Prompt injection attacks capable of fabricating candidate evaluation scores or evidence.

**Testing Notice:** Please test against a local deployment (using offline mock mode) rather than hosted instances with real user data.

---

## 🛡️ Production Deployment Safeguards

When deploying your own instance:
* Set `JWT_SECRET_KEY` to a cryptographically random secret (`python3 -c "import secrets; print(secrets.token_urlsafe(32))"`).
* Enable authentication with `AUTH_ENABLED=true`.
* Provide a durable PostgreSQL database via `DATABASE_URL`.
* Restrict `CORS_ALLOW_ORIGINS` to trusted frontend domains.
