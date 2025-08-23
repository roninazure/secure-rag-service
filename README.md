# PrivateGPT • Secure RAG Service

[🚀 Pilot Request](../../issues/new?template=pilot-request.yml&title=Pilot+Request+%5BSep+13%5D)
[📄 One-Pager](../../releases/latest/download/PrivateGPT_OnePager.pdf) ·
[📇 vCard](../../releases/latest/download/Scott_Steele.vcf) ·
[🧪 3-min Demo](#run-a-3-minute-demo) ·
[💬 Ask a Question](../../discussions/new?category=q-a) ·
[▶️ Open in Codespaces](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=roninazure%2Fsecure-rag-service) ·
[🚀 Pilot Request](../../issues/new?template=pilot-request.md&labels=lead,event-sep13)


# Secure RAG Service (NexusAI)

A production-ready Retrieval-Augmented Generation (RAG) backend with a simple chat API.  
Built with **FastAPI + Uvicorn**, vector search (Pinecone), and **AWS Bedrock (Titan)** for embeddings and text. Designed to sit behind **Nginx** and serve a React UI (optional) via `/`, proxying API calls at `/api/*`.

> **Status:** Pilot VM live on EC2. HTTPS enabled (self-signed for pilot). RAG operational.

---

## Features
- **Clean API**: `/api/chat/`, `/api/status`, `/api/ingest`, `/health`
- **RAG pipeline**: Pinecone (1024-dim), Bedrock Titan embeddings + text gen
- **Deployable**: Nginx reverse proxy, systemd unit, TLS (self-signed or ACM)
- **Tested**: Pytest suite + GitHub Actions CI (Python)
- **Security posture**: private backend on loopback, TLS at the edge, keys via env/SSM/Secrets Manager

---

## Quick Start

### Requirements
- Python **3.11+**
- An API key for **Pinecone**, and AWS credentials with Bedrock access
- (Optional) React UI build to be served by Nginx

### Install & Run (local)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Create your environment file
cat > .env <<'ENV'
AWS_REGION=us-east-1
PINECONE_API_KEY=replace-me
PINECONE_INDEX=secure-rag
EMBEDDING_MODEL=amazon.titan-embed-text-v2:0
TEXT_MODEL=amazon.titan-text-express-v1
SIMILARITY_THRESHOLD=0.30
TOP_K=7
ENV

# Start API
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

Health a& Smoke
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:8000/api/status
curl -s -X POST http://127.0.0.1:8000/api/chat/ \
  -H 'Content-Type: application/json' \
  -d '{"message":"hello"}'

API (minimal)
	•	GET /health → { "status": "healthy" }
	•	GET /api/status → vector DB + model config snapshot
	•	POST /api/chat/ → { id, role, content, timestamp }
	•	POST /api/ingest → push docs into the index (see code for schema)

⸻

Deploy (EC2 gist)
	1.	Backend runs on 127.0.0.1:8000 via systemd (no public bind).
	2.	Nginx serves UI at /, proxies /api/* → http://127.0.0.1:8000.
	3.	TLS: self-signed for pilot or real cert via ACM/Let’s Encrypt.
	4.	Secrets: load via environment, SSM Parameter Store, or Secrets Manager.

See infra/ for IaC starters and SECURITY.md for disclosure policy.

⸻

Security, License, Trademarks
	•	Security policy: SECURITY.md
	•	License: MIT (see LICENSE)
	•	Trademarks: TRADEMARKS.md — NexusAI™ is a trademark of Scott Steele
	•	Third-party notices: THIRD_PARTY_BACKEND.md, THIRD_PARTY_FRONTEND.json

⸻

Contributing

PRs welcome. By contributing you agree to the MIT license and to follow the guidance in CONTRIBUTING.md. Add/update third-party notices when adding deps.

© 2025 Scott Steele. All rights reserved.
