from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Any
import os
import json
import time
import uuid

from backend.telemetry import build_demo_incident
from backend.retrieval import retrieve_evidence
from backend.safety import evaluate_action
from backend.lyzr_client import call_lyzr

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]

app = FastAPI(
    title="SentinelOps AI",
    version="0.1.0"
)


class AnalyzeRequest(BaseModel):
    incident_id: str = "INC-2026-0911-001"


class ApprovalRequest(BaseModel):
    approved: bool


@app.get("/")
def index():
    return FileResponse(ROOT / "frontend" / "index.html")


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "lyzr_enabled": os.getenv(
            "LYZR_ENABLED",
            "false"
        ).lower() == "true"
    }


@app.get("/api/demo")
def demo():
    return build_demo_incident()


@app.post("/api/analyze")
def analyze(req: AnalyzeRequest):
    incident = build_demo_incident(req.incident_id)

    t0 = time.perf_counter()

    # ---------------------------------------------------------
    # 1. TRIAGE AGENT
    # ---------------------------------------------------------
    triage = call_lyzr(
        "triage",
        incident
    )

    # ---------------------------------------------------------
    # 2. EVIDENCE RETRIEVAL
    # ---------------------------------------------------------
    evidence = retrieve_evidence(
        incident,
        triage
    )

    # ---------------------------------------------------------
    # 3. DIAGNOSTIC AGENT
    # ---------------------------------------------------------
    diagnostic_input = {
        "incident": incident,
        "triage": triage,
        "evidence": evidence
    }

    diagnosis = call_lyzr(
        "diagnostic",
        diagnostic_input
    )

    # ---------------------------------------------------------
    # 4. RUNBOOK SELECTION
    # ---------------------------------------------------------
    runbook_id = diagnosis.get(
        "recommended_runbook_id",
        "RB-CHECKOUT-ROLLBACK"
    )

    runbook = next(
        (
            x
            for x in evidence["runbooks"]
            if x["id"] == runbook_id
        ),
        evidence["runbooks"][0]
    )

    # ---------------------------------------------------------
    # 5. REMEDIATION AGENT
    # ---------------------------------------------------------
    remediation = call_lyzr(
        "remediation",
        {
            "diagnosis": diagnosis,
            "runbook": runbook,
            "approved_actions": evidence["approved_actions"]
        }
    )

    # ---------------------------------------------------------
    # 6. SAFETY GATE
    # ---------------------------------------------------------
    safety = evaluate_action(
        remediation
    )

    total_ms = round(
        (time.perf_counter() - t0) * 1000
    )

    # ---------------------------------------------------------
    # 7. AUDIT TRAIL
    # ---------------------------------------------------------
    audit = [
        {
            "step": "ALERT_INGEST",
            "status": "complete"
        },
        {
            "step": "TRIAGE",
            "status": "complete"
        },
        {
            "step": "EVIDENCE_RETRIEVAL",
            "status": "complete"
        },
        {
            "step": "DIAGNOSIS",
            "status": "complete"
        },
        {
            "step": "SAFETY_GATE",
            "status": safety["status"]
        },
        {
            "step": "HITL",
            "status": "pending"
        }
    ]

    # ---------------------------------------------------------
    # 8. RESPONSE
    # ---------------------------------------------------------
    return {
        "incident": incident,
        "triage": triage,
        "evidence": evidence,
        "diagnosis": diagnosis,
        "remediation": remediation,
        "safety": safety,
        "audit": audit,
        "hitl_required": True,
        "performance": {
            "latency_ms": total_ms,
            "estimated_raw_log_lines": 100000,
            "retrieved_log_lines": len(
                evidence["logs"]
            ),
            "estimated_token_reduction_pct": 92
        }
    }


@app.post("/api/approve")
def approve(req: ApprovalRequest):

    # ---------------------------------------------------------
    # HUMAN REJECTS REMEDIATION
    # ---------------------------------------------------------
    if not req.approved:
        return {
            "status": "rejected",

            "message": (
                "HITL approval denied. "
                "No remediation executed."
            ),

            "hitl_status": "REJECTED",

            "audit_status": "HITL_REJECTED",

            "remediation_status": "NOT_EXECUTED",

            "recovery": {
                "error_rate": "18.7%",
                "memory": "94%",
                "service": "INCIDENT_ACTIVE"
            }
        }

    # ---------------------------------------------------------
    # HUMAN APPROVES REMEDIATION
    # ---------------------------------------------------------
    return {
        "status": "executed",

        "message": (
            "Rollback simulated successfully. "
            "No destructive infrastructure mutation "
            "was performed."
        ),

        "hitl_status": "APPROVED",

        "audit_status": "HITL_APPROVED",

        "remediation_status": "SIMULATED_SUCCESS",

        "recovery": {
            "error_rate": "2.1%",
            "memory": "61%",
            "service": "HEALTHY"
        }
    }


@app.post("/api/lyzr/test")
def lyzr_test():
    return call_lyzr(
        "triage",
        build_demo_incident()
    )
