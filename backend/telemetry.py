from datetime import datetime, timezone

def build_demo_incident(incident_id="INC-2026-0911-001"):
    return {
        "incident_id": incident_id,
        "timestamp": "2026-09-11T10:14:32+05:30",
        "severity_hint": "P1",
        "service": "checkout-api",
        "alerts": [
            {"id":"ALT-001","source":"prometheus","metric":"error_rate","value":18.7,"unit":"%","baseline":1.2},
            {"id":"ALT-002","source":"prometheus","metric":"latency_p95","value":4.8,"unit":"s","baseline":0.8},
            {"id":"ALT-003","source":"kubernetes","metric":"pod_restarts","value":14,"baseline":0},
            {"id":"ALT-004","source":"prometheus","metric":"memory","value":94,"unit":"%","baseline":52},
        ],
        "deployment": {
            "id":"DEP-4821",
            "version":"checkout-v4821",
            "service":"checkout-api",
            "timestamp":"2026-09-11T10:06:12+05:30"
        },
        "logs": [
            {"id":"LOG-001","time":"10:07:01","text":"checkout-api heap usage rising after startup"},
            {"id":"LOG-002","time":"10:09:42","text":"worker allocation failed; retrying"},
            {"id":"LOG-003","time":"10:10:18","text":"request timeout threshold exceeded"},
            {"id":"LOG-004","time":"10:11:02","text":"pod restarted due to memory pressure"},
            {"id":"LOG-005","time":"10:12:27","text":"pod restarted due to memory pressure"},
        ],
        "historical_incidents": [
            {"id":"INC-HIST-17","summary":"checkout-api memory growth after release","matching_signals":["memory pressure","worker allocation","pod restart"]}
        ]
    }
