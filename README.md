# SentinelOps AI

Governed Cloud Incident Triage & Runbook Remediation Agent for the Lyzr Agent Arena.

## Architecture

Alert Ingest → Triage → Evidence Retrieval → Diagnosis → Safety Gate → HITL → Remediation → RCA → Audit Timeline

## Required structure

- `agents/` — Lyzr agent prompts/configuration
- `backend/` — FastAPI orchestration, telemetry, retrieval, safety, Lyzr client
- `frontend/` — lightweight dashboard
- `data/` — synthetic telemetry and runbooks

## Quick start

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Open http://localhost:8000

## Lyzr setup

Copy `.env.example` to `.env` and add the Lyzr API key and agent IDs after creating the agents in Lyzr Studio.

The app runs in safe demo/mock mode when `LYZR_ENABLED=false`, so the complete UX can be tested without secrets.

Lyzr's current Agent API uses the `https://agent-prod.studio.lyzr.ai/` API server and v3 inference endpoints. See the official docs:
https://docs.lyzr.ai/agent-api/introduction
