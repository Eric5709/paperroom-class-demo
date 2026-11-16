# PAPER ROOM v3 — Submission Demo

Single-page research collaboration demo built with HTML/CSS/vanilla JS and a Python web server. It includes a rich, automatically seeded public demo for URL submissions, private token-based projects, invitations, Fig/Table editing, timestamped immutable revisions, notes, diff/compare, rollback-as-new-revision, tasks, comments and logs.

See **[SUBMISSION_GUIDE_KO.md](SUBMISSION_GUIDE_KO.md)** for exact Render Free deployment and optional Neon persistent PostgreSQL instructions.

**Start locally:** `python3 server.py` → http://127.0.0.1:8765

**Environment:** `PORT`, `HOST`, `BASE_URL`, `DEMO_READONLY`, `PAPERROOM_DATA_DIR`, `DATABASE_URL` (optional external PostgreSQL), `SMTP_*` (optional). `render.yaml` uses only the free web service, no paid persistent disk.

**Tests:** `python3 tests/test_smoke.py && python3 tests/test_versions.py`. Local SQLite path is fully tested; external PostgreSQL must be verified against a real hosted connection before production use.

**Security & limitations:** This is for class demonstrations and low-risk collaboration. Invitations are bearer links without email verification; owner links are sensitive. Free Render local data is ephemeral and is reset on sleep/restart; only the seeded public demo reappears automatically. External PostgreSQL is needed to persist real edits and version history across restarts. No rate limiting, SSO, encrypted file storage, automatic off-site backups or real-time editing conflict resolution (other than version compare-and-swap for saves) is implemented.
