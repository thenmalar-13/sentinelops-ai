import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def retrieve_evidence(incident, triage=None):
    runbooks = [
        {
            "id":"RB-CHECKOUT-ROLLBACK",
            "title":"Checkout release rollback",
            "risk":"LOW",
            "reversible":True,
            "approved":True,
            "action":"Rollback the checkout deployment to the previous known-good version."
        },
        {
            "id":"RB-SCALE-CHECKOUT",
            "title":"Scale checkout pods",
            "risk":"LOW",
            "reversible":True,
            "approved":True,
            "action":"Increase checkout-api replicas using the approved scaling procedure."
        }
    ]
    # Simple deterministic retrieval for the MVP: select evidence matching the incident signals.
    relevant_logs = [
        x for x in incident["logs"]
        if any(k in x["text"].lower() for k in ["heap","allocation","timeout","memory","restart"])
    ]
    return {
        "logs": relevant_logs,
        "deployment": incident["deployment"],
        "historical_incidents": incident["historical_incidents"],
        "runbooks": runbooks,
        "approved_actions": [r["id"] for r in runbooks if r["approved"]],
        "retrieval_method":"deterministic keyword + metadata retrieval"
    }
