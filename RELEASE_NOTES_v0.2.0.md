# v0.2.0 — EC2 Pilot: Frontend + Backend + Infra + Legal

## Highlights
- ✅ Live pilot on AWS EC2 (Amazon Linux 2023, t2.micro) behind Nginx (HTTP→HTTPS), self-signed TLS.
- ✅ RAG online: Pinecone (1024-dim) + Bedrock Titan (embed + text).
- ✅ Unified build: React UI uses relative `/api/*` paths; same bundle works locally and on EC2.
- ✅ Systemd service for FastAPI/Uvicorn on `127.0.0.1:8000`.

## What’s New
- Frontend: Chat UI send arrow, dark mode, Vite proxy, static build.
- Backend: FastAPI endpoints (`/api/chat/`, `/api/status`, `/health`) and RAG wiring.
- Nginx: Static `/`, proxy `/api/` → `127.0.0.1:8000`, `/health` → backend.
- Infra (pilot): EC2 setup scripts, nginx config, self-signed cert bootstrap.
- Legal/Security: LICENSE, NOTICE, COPYRIGHT, TRADEMARKS.md, SECURITY.md,
  THIRD_PARTY_BACKEND.md, THIRD_PARTY_FRONTEND.json.
- Repo hygiene: modern .gitignore, updated README.

## Known Risks (pilot)
Self-signed TLS warning; no auth; single instance; manual deploy; limited corpus.

## Upgrade Notes
1) Pull latest main.
2) Build UI: `cd frontend && npm ci && npm run build`.
3) `scp dist.tgz` to EC2.
4) Unpack to `/var/www/nexusai`, reload nginx; ensure `privategpt-backend.service` is active.

## Next
AuthN/Z, real TLS + domain, CloudWatch, CI/CD, ingestion pipeline, history persistence.
