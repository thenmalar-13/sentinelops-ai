
import json
import os
import re
import time
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
    """
    Convert a Lyzr response into a Python dictionary.

    Handles:
    1. Already-parsed dictionaries
    2. JSON strings
    3. Markdown fenced JSON
    4. JSON embedded inside surrounding text
    5. Nested {"raw_response": "..."} responses
    """

    if isinstance(value, dict):
        # If Lyzr wrapped the actual JSON in raw_response,
        # unwrap it.
        if "raw_response" in value and len(value) == 1:
            return _extract_json(value["raw_response"])

        return value

    if not isinstance(value, str):
        return {"raw_response": value}

    text = value.strip()

    # Remove markdown fences.
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)

    # Direct JSON parse.
    try:
        parsed = json.loads(text)

        if isinstance(parsed, dict):
            if "raw_response" in parsed and len(parsed) == 1:
                return _extract_json(parsed["raw_response"])

            return parsed

    except json.JSONDecodeError:
        pass

    # Try to find an embedded JSON object.
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end > start:
        candidate = text[start:end + 1]

        try:
            parsed = json.loads(candidate)

            if isinstance(parsed, dict):
                if "raw_response" in parsed and len(parsed) == 1:
                    return _extract_json(parsed["raw_response"])

                return parsed

        except json.JSONDecodeError:
            pass

    # Could not parse it.
    return {"raw_response": value}


def _normalise_agent_response(response):
    """
    Lyzr's API may return the agent's JSON inside different
    wrapper fields. Keep unwrapping until the actual agent
    object is obtained.
    """

    result = response

    # Unwrap common API wrappers.
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

                # Prefer the parsed object when it contains
                # meaningful agent fields.
                if isinstance(parsed, dict):
                    result = parsed
                    break

    result = _extract_json(result)

    return result


def call_lyzr(kind, prompt):
    """
    Call one Lyzr agent.

    When LYZR_ENABLED=false, deterministic mock mode is used
    and no Lyzr credits are consumed.

    When LYZR_ENABLED=true, the real Lyzr agent is called.
    """

    if not LYZR_ENABLED:
        return {
            "_meta": {
                "provider": "mock",
                "agent": kind,
            }
        }

    agent_id = AGENT_IDS.get(kind)

    if not LYZR_API_KEY:
        raise RuntimeError("LYZR_API_KEY is not configured")

    if not LYZR_USER_ID:
        raise RuntimeError("LYZR_USER_ID is not configured")

    if not agent_id:
        raise RuntimeError(
            f"Lyzr agent ID is not configured for {kind}"
        )

    url = f"{LYZR_BASE_URL}/v3/inference/chat/"

    payload = {
        "user_id": LYZR_USER_ID,
        "agent_id": agent_id,
        "message": prompt,
    }

    headers = {
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

        response.raise_for_status()

    except requests.RequestException as exc:
        elapsed_ms = round(
            (time.perf_counter() - started) * 1000
        )

        raise RuntimeError(
            f"Lyzr {kind} request failed after "
            f"{elapsed_ms}ms: {exc}"
        ) from exc

    try:
        api_response = response.json()
    except ValueError as exc:
        raise RuntimeError(
            f"Lyzr {kind} returned a non-JSON response"
        ) from exc

    parsed = _normalise_agent_response(api_response)

    if not isinstance(parsed, dict):
        raise RuntimeError(
            f"Lyzr {kind} response could not be converted to an object"
        )

    parsed["_meta"] = {
        "provider": "lyzr",
        "agent": kind,
        "agent_id": agent_id,
        "latency_ms": round(
            (time.perf_counter() - started) * 1000
        ),
    }

    return parsed

