from backend.safety import evaluate_action

def test_blocks_destructive_action():
    result = evaluate_action({"action":"DROP DATABASE"})
    assert result["status"] == "BLOCKED"

def test_requires_hitl():
    result = evaluate_action({"action":"Rollback deployment","requires_human_approval":True})
    assert result["status"] == "HITL_REQUIRED"
