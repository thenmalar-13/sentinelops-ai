import os, uuid, requests

BASE = os.getenv("LYZR_BASE_URL", "https://agent-prod.studio.lyzr.ai").rstrip("/")
ENABLED = os.getenv("LYZR_ENABLED", "false").lower() == "true"
API_KEY = os.getenv("LYZR_API_KEY", "")

AGENT_IDS = {
    "triage": os.getenv("LYZR_TRIAGE_AGENT_ID",""),
    "diagnostic": os.getenv("LYZR_DIAGNOSTIC_AGENT_ID",""),
    "remediation": os.getenv("LYZR_REMEDIATION_AGENT_ID",""),
    "rca": os.getenv("LYZR_RCA_AGENT_ID",""),
}

def _mock(kind, payload):
    if kind == "triage":
        return {
            "severity":"P1",
            "service":"checkout-api",
            "summary":"Checkout service is degraded with elevated errors, latency, memory and pod restarts.",
            "signals":[
                {"source_id":"ALT-001","fact":"Error rate is 18.7%, baseline 1.2%."},
                {"source_id":"ALT-004","fact":"Memory is 94%, baseline 52%."},
                {"source_id":"DEP-4821","fact":"checkout-v4821 deployed 8 minutes before incident."}
            ],
            "hypotheses":[
                {"hypothesis":"Memory leak introduced by recent checkout deployment","confidence":94,"evidence_ids":["ALT-004","LOG-001","LOG-004","DEP-4821"]}
            ],
            "requires_more_evidence":False
        }
    if kind == "diagnostic":
        return {
            "root_cause":"Probable memory leak introduced by checkout-v4821.",
            "confidence":94,
            "evidence":[
                {"id":"ALT-004","reason":"Memory rose from 52% baseline to 94%."},
                {"id":"LOG-001","reason":"Heap usage began rising after startup."},
                {"id":"LOG-004","reason":"Pod restarted due to memory pressure."},
                {"id":"DEP-4821","reason":"Recent deployment precedes the observed degradation."}
            ],
            "alternative_hypotheses":["Traffic spike","Downstream timeout cascade"],
            "recommended_runbook_id":"RB-CHECKOUT-ROLLBACK",
            "human_review_required":False
        }
    if kind == "remediation":
        return {
            "status":"PROPOSED",
            "runbook_id":"RB-CHECKOUT-ROLLBACK",
            "action":"Rollback the checkout deployment to the previous known-good version.",
            "risk":"LOW",
            "requires_human_approval":True,
            "reason":"Reversible approved runbook matched the evidence-backed diagnosis.",
            "blocked_actions":["DROP DATABASE","DELETE POD","REBOOT CLUSTER"]
        }
    if kind == "rca":
        return {
            "title":"P1 Checkout API degradation",
            "impact":"Elevated checkout errors and latency.",
            "root_cause":"Probable memory leak introduced by checkout-v4821.",
            "timeline":[],
            "remediation":"Rollback checkout-v4821 after human approval.",
            "prevention":["Add memory regression checks to deployment validation."],
            "evidence_ids":["ALT-004","LOG-001","LOG-004","DEP-4821"]
        }
    return {}

def call_lyzr(kind, payload):
    agent_id = AGENT_IDS.get(kind, "")
    if not ENABLED or not API_KEY or not agent_id:
        return _mock(kind, payload)

    url = f"{BASE}/v3/inference/chat/"
    body = {
        "user_id": os.getenv("LYZR_USER_ID","sentinelops-demo"),
        "agent_id": agent_id,
        "session_id": f"sentinelops-{uuid.uuid4()}",
        "message": str(payload),
        "system_prompt_variables": {},
        "filter_variables": {},
        "features": []
    }
    r = requests.post(url, json=body, headers={
        "x-api-key": API_KEY,
        "Content-Type":"application/json"
    }, timeout=30)
    r.raise_for_status()
    data = r.json()
    # Lyzr chat responses may return a string under response.
    return {"raw_response": data.get("response", data)}
