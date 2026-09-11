DANGEROUS = {
    "delete","drop","destroy","format","terminate","wipe","shutdown","reboot_cluster"
}

def evaluate_action(remediation):
    text = str(remediation.get("action","")).lower()
    blocked = [word for word in DANGEROUS if word in text]
    if blocked:
        return {
            "status":"BLOCKED",
            "reason":"Potentially destructive action detected by safety policy.",
            "blocked_terms":blocked
        }
    if remediation.get("requires_human_approval", True):
        return {
            "status":"HITL_REQUIRED",
            "reason":"Approved reversible remediation requires explicit human approval.",
            "blocked_terms":[]
        }
    return {"status":"ALLOWED","reason":"Action passed policy checks.","blocked_terms":[]}
