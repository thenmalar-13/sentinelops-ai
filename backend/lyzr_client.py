import json
import os
import re
import time
import uuid
import requests

LYZR_ENABLED = os.getenv("LYZR_ENABLED", "false").lower() == "true"

LYZR_API_KEY = os.getenv("LYZR_API_KEY", "")
LYZR_USER_ID = os.getenv("LYZR_USER_ID", "")

LYZR_BASE_URL = os.getenv(
    "LYZR_BASE_URL",
    "https://agent-prod.studio.lyzr.ai"
).rstrip("/")

AGENT_IDS = {
    "triage": os.getenv("LYZR_TRIAGE_AGENT_ID", ""),
    "diagnostic": os.getenv("LYZR_DIAGNOSTIC_AGENT_ID", ""),
    "remediation": os.getenv("LYZR_REMEDIATION_AGENT_ID", ""),
    "rca": os.getenv("LYZR_RCA_AGENT_ID", ""),
}


def _extract_json(value):
    if isinstance(value, dict):
        if "raw_response" in value and len(value) == 1:
            return _extract_json(value["raw_response"])
        return value

    if not isinstance(value, str):
        return {"raw_response": value}

    text = value.strip()

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )
    text = re.sub(r"\s*```$", "", text)

    try:
        parsed = json.loads(text)

        if isinstance(parsed, dict):
            if "raw_response" in parsed and len(parsed) == 1:
                return _extract_json(parsed["raw_response"])
            return parsed

    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end > start:
        candidate = text[start:end + 1]

        try:
            parsed = json.loads(candidate)

            if isinstance(parsed, dict):
                return parsed

        except json.JSONDecodeError:
            pass

    return {"raw_response": value}


def _normalise_agent_response(response):
    result = response

    if isinstance(result, dict):

        for key in (
            "response",
            "message",
            "content",
            "output",
            "data",
            "result",
        ):

            value = result.get(key)

            if isinstance(value, (dict, str)):
                parsed = _extract_json(value)

                if isinstance(parsed, dict):
                    result = parsed
                    break

    return _extract_json(result)


def call_lyzr(kind, prompt):

    # -----------------------------------------
    # LOCAL / ZERO-CREDIT MODE
    # -----------------------------------------

    if not LYZR_ENABLED:
        return {
            "_meta": {
                "provider": "mock",
                "agent": kind,
            }
        }

    # -----------------------------------------
    # VALIDATION
    # -----------------------------------------

    agent_id = AGENT_IDS.get(kind)

    if not LYZR_API_KEY:
        raise RuntimeError("LYZR_API_KEY is not configured")

    if not LYZR_USER_ID:
        raise RuntimeError("LYZR_USER_ID is not configured")

    if not agent_id:
        raise RuntimeError(
            f"Lyzr agent ID is not configured for {kind}"
        )

    # -----------------------------------------
    # CURRENT LYZR V3 ENDPOINT
    # -----------------------------------------

    url = f"{LYZR_BASE_URL}/v3/inference/chat/"

    # Lyzr v3 requires a session_id.
    session_id = f"{agent_id}-{uuid.uuid4().hex[:16]}"

    payload = {
        "user_id": LYZR_USER_ID,
        "agent_id": agent_id,
        "session_id": session_id,
        "message": json.dumps(prompt, indent=2),
        "system_prompt_variables": {},
        "filter_variables": {},
        "features": [],
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "x-api-key": LYZR_API_KEY,
    }

    started = time.perf_counter()

    try:

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=(10, 30),
        )

        elapsed_ms = round(
            (time.perf_counter() - started) * 1000
        )

        # IMPORTANT:
        # Preserve the actual Lyzr response body
        # when an API error occurs.
        if not response.ok:

            body = response.text[:2000]

            raise RuntimeError(
                f"Lyzr {kind} request failed "
                f"after {elapsed_ms}ms "
                f"(HTTP {response.status_code}): "
                f"{body}"
            )

    except requests.RequestException as exc:

        elapsed_ms = round(
            (time.perf_counter() - started) * 1000
        )

        raise RuntimeError(
            f"Lyzr {kind} network request failed "
            f"after {elapsed_ms}ms: {exc}"
        ) from exc

    # -----------------------------------------
    # PARSE RESPONSE
    # -----------------------------------------

    try:
        api_response = response.json()

    except ValueError as exc:

        raise RuntimeError(
            f"Lyzr {kind} returned a non-JSON response: "
            f"{response.text[:1000]}"
        ) from exc

    parsed = _normalise_agent_response(api_response)

    if not isinstance(parsed, dict):

        raise RuntimeError(
            f"Lyzr {kind} response could not be "
            f"converted into an object"
        )

    parsed["_meta"] = {
        "provider": "lyzr",
        "agent": kind,
        "agent_id": agent_id,
        "session_id": session_id,
        "latency_ms": round(
            (time.perf_counter() - started) * 1000
        ),
    }

    return parsed
