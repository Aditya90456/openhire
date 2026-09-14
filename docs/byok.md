# Bring Your Own Key (BYOK)

A candidate can save their own LLM provider API key on their profile page
(`pages/profile.html`, "API Keys" card). The credential storage, encryption,
and API are provider-agnostic infrastructure, but access is candidate-only
and the supported provider is currently narrowed to Gemini (see "Supported
providers" below).

**Not yet wired to any candidate-facing LLM call.** The recruiter-side
context wiring built earlier (`apply_llm_context_for_recruiter`,
`api/dependencies.py`) resolves a saved credential via the job's *owning
recruiter* for job description analysis (`POST /jobs`), resume matching
(`POST /jobs/{job_id}/match`), and post-interview evaluation. Under this
candidate-only access model, recruiters can never have a saved credential,
so that wiring will simply never find one to use — those calls always run
on OpenHire's system key now. Connecting a candidate's saved key to an
actual candidate-facing LLM call path (e.g. interview question generation)
is a documented follow-up, **not yet implemented**. Resume parsing on
upload also still uses OpenHire's system key, as before.

## Enabling it

Set `BYOK_ENCRYPTION_KEY` to a Fernet key:

```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Unset (the default), BYOK is completely inert: the credential table is
never read, and the profile page shows an explanatory placeholder instead
of the form.

## Supported providers

Gemini only, for now. The underlying provider infrastructure
(`build_provider`, the Postgres schema's CHECK constraint) still supports
all four native providers (`openai`, `gemini`, `groq`, `nvidia_nim`), but
API-level request validation and the profile page's UI are deliberately
narrowed to `gemini` — the other three can be re-enabled later without a
schema migration. No `litellm`-style universal routing regardless.

## API

- `GET /auth/me/llm-credential` → `{provider, model, key_hint, status,
  last_error, last_error_at}`, or `204` when none is saved.
- `PUT /auth/me/llm-credential` → body `{provider, api_key, model?}`. Makes
  one live validation call before saving; a bad key returns `400` and
  writes nothing.
- `DELETE /auth/me/llm-credential` → removes the credential; the account
  reverts to OpenHire's system key.

All three require an authenticated candidate principal (`require_candidate`)
— a recruiter or admin gets `403`. None of them ever returns the key itself.

## Key handling

The key is encrypted at rest (`cryptography.Fernet`) and decrypted only in
memory, for the duration of one provider construction. It is never logged,
never included in any API response, never written to an `AuditLog` entry,
and the profile page never writes it to `localStorage`, `sessionStorage`,
or a cookie.

## Failure behaviour

If a saved key stops working (revoked, rate-limited), that one call falls
back to OpenHire's system key automatically and the credential is marked
`status: "failed"` with `last_error` — surfaced on the profile page. (This
fallback mechanism is exercised today only by the still-recruiter-wired
call sites described above, since those never actually resolve a
candidate's credential under the current access model.)

## Supersedes

This replaces the August design in `docs/superpowers/specs/2026-08-25-byok-design.md`
and `docs/superpowers/plans/2026-08-25-byok.md`, written when OpenAI was
the only provider and before a real accounts system existed. See
`docs/superpowers/specs/2026-09-06-byok-design.md` for the full design
this implementation follows.
