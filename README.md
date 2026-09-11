# 🛡️ SentinelOps AI

### Governed Multi-Agent Cloud Incident Triage & Safe Remediation

> **Evidence-grounded incident response for cloud/SRE teams — with retrieval, specialized Lyzr agents, safety enforcement, human approval, and automated blameless RCA.**

[![Lyzr](https://img.shields.io/badge/Lyzr-Live%20Agents-ffbd2e)](https://www.lyzr.ai/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED)](https://www.docker.com/)
[![Status](https://img.shields.io/badge/Status-Live-success)](https://sentinelops-ai-3.onrender.com)

## 🚀 Live Demo

### [▶ Launch SentinelOps AI](https://sentinelops-ai-3.onrender.com)

**Execution mode:** LYZR LIVE
**Scenario:** Synthetic P1 `checkout-api` production incident
**Agents:** Triage → Diagnosis → Remediation → RCA

---

# 🎯 Problem

Cloud incidents generate large volumes of noisy alerts, logs, and telemetry.

During a P1 incident, an SRE needs to answer:

* What is actually happening?
* Which alerts belong to the same incident?
* What is the most likely root cause?
* Which evidence supports that conclusion?
* What remediation is safe?
* Can automation be trusted to change production?
* How can the incident be documented afterward?

A conventional script can execute commands, but unsafe automation can make an incident worse.

**SentinelOps AI approaches incident response as a governed multi-agent decision system rather than an unrestricted automation bot.**

---

# 💡 Solution

SentinelOps AI creates a specialized SRE agent mesh that:

1. Ingests a structured cloud incident.
2. Triages severity and affected service.
3. Retrieves the most relevant evidence.
4. Diagnoses the probable root cause using evidence IDs.
5. Checks remediation against safety rules.
6. Blocks destructive operations.
7. Requires explicit human approval for production-changing remediation.
8. Generates an automated blameless post-mortem.

### Core principle

> **AI can investigate and recommend. Humans remain in control of production-changing actions.**

---

# 🏗️ Architecture

```text
┌──────────────────────────────┐
│      Alert Ingestion         │
│ Prometheus/Kubernetes-style  │
│         telemetry            │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       Lyzr Triage Agent      │
│ Severity • Service • Signals │
│ Hypotheses • Deduplication   │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│      Evidence Retrieval      │
│ Relevant logs • telemetry    │
│ deployments • history        │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│     Lyzr Diagnostic Agent    │
│ Root Cause • Confidence      │
│ Evidence • Alternatives      │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│        Safety Gate           │
│ Approved runbooks + policy   │
│ Destructive actions blocked  │
└──────────────┬───────────────┘
               │
          ┌────┴────┐
          │         │
          ▼         ▼
     BLOCKED       HITL
   Destructive   Human Approval
     Actions         │
                     ▼
             ┌───────────────┐
             │  Remediation  │
             │ Safe /        │
             │ Reversible    │
             └───────┬───────┘
                     │
                     ▼
             ┌───────────────┐
             │  Lyzr RCA     │
             │ Blameless     │
             │ Post-Mortem   │
             └───────────────┘
```

---

# 🤖 Multi-Agent Design

SentinelOps uses four specialized Lyzr agents rather than one unrestricted agent.

| Agent                     | Responsibility                              | Safety Boundary                        |
| ------------------------- | ------------------------------------------- | -------------------------------------- |
| 🔎 **Triage Agent**       | Severity, service, signals, hypotheses      | No remediation                         |
| 🧠 **Diagnostic Agent**   | Evidence-grounded root-cause analysis       | Cannot invent evidence/runbooks        |
| 🛡️ **Remediation Agent** | Select approved safe/reversible remediation | Cannot execute infrastructure          |
| 📋 **RCA Agent**          | Blameless post-mortem and timeline          | Must distinguish facts from hypotheses |

### Why multiple agents?

Each agent has a narrow responsibility and constrained prompt architecture.

This reduces the risk of an unrestricted model both diagnosing an incident and deciding to execute a potentially destructive operation.

---

# 🧠 Evidence-Grounded Diagnosis

SentinelOps does not ask the diagnostic agent to reason from an unrestricted raw telemetry dump.

The pipeline first selects relevant evidence.

```text
Large telemetry context
        │
        ▼
Evidence Retrieval
        │
        ├── Deployment signals
        ├── Memory telemetry
        ├── Restart events
        ├── Application logs
        └── Historical incidents
        │
        ▼
Relevant evidence
        │
        ▼
Diagnostic Agent
```

Every important diagnostic claim is required to reference supplied evidence IDs.

Example:

```text
DEP-4821
LOG-001
LOG-004
LOG-005
```

This creates an auditable evidence chain between the incident signals and the diagnosis.

---

# 🔥 Demonstrated Incident

The included synthetic incident represents a P1 `checkout-api` failure.

### Observed signals

| Signal       |            Current |         Baseline |
| ------------ | -----------------: | ---------------: |
| Error rate   |          **18.7%** |             1.2% |
| Memory       |            **94%** |              52% |
| Latency      |           Elevated |    0.8s baseline |
| Pod restarts |             **14** |                0 |
| Deployment   | **checkout-v4821** | Previous version |

Relevant logs include:

```text
LOG-001  checkout-api heap usage rising after startup
LOG-002  worker allocation failed; retrying
LOG-003  request timeout threshold exceeded
LOG-004  pod restarted due to memory pressure
LOG-005  pod restarted due to memory pressure
```

The diagnostic agent correlates these signals with deployment `DEP-4821` and identifies a probable memory-growth / memory-pressure regression.

### Demonstrated diagnosis

**Root cause:** probable memory-growth / memory-pressure regression introduced by `DEP-4821`.

**Confidence:** 95%

**Alternative hypotheses are preserved rather than discarded**, including worker exhaustion and insufficient replica capacity.

---

# 🛡️ Safety-First Remediation

SentinelOps deliberately separates **recommendation** from **execution**.

### Destructive actions are blocked

```text
❌ DROP DATABASE
❌ DELETE POD
❌ REBOOT CLUSTER
```

### Safe remediation

For the demonstrated incident, the recommended action is:

```text
Rollback checkout deployment
→ Previous known-good version
→ LOW risk
→ Human approval required
```

The system never gives the Lyzr agent unrestricted infrastructure execution capability.

---

# 👤 Human-in-the-Loop (HITL)

Production-changing remediation requires explicit human approval.

```text
Diagnostic Agent
       │
       ▼
Remediation Proposal
       │
       ▼
Safety Gate
       │
       ├───────────────► Destructive → BLOCK
       │
       ▼
Human Approval
       │
    ┌──┴──┐
    ▼     ▼
 Approve Reject
    │     │
    ▼     ▼
Simulated  Stop
Execution  Action
```

The MVP intentionally uses a **simulated execution layer**.

No real production infrastructure is modified.

This makes the demonstration safe while preserving the governance architecture required for a real SRE deployment.

---

# 📚 Retrieval & Context Optimization

The system retrieves relevant evidence before sending incident context into the reasoning pipeline.

For the synthetic demonstration:

> **92% context reduction**

The optimization is measured as context reduction from the simulated raw telemetry volume to the selected evidence context.

### Why this matters

Reducing irrelevant context can:

* reduce token consumption,
* reduce unnecessary model processing,
* improve signal-to-noise ratio,
* improve latency potential,
* make diagnostic reasoning more focused.

**Note:** The 92% figure represents demonstrated context reduction in the synthetic scenario, not a claim of 92% monetary cost savings.

---

# 🧩 Prompt Architecture & Hallucination Mitigation

The agents use constrained role-specific prompts.

### Triage constraints

* Use only supplied information.
* Do not invent metrics, logs, deployments, or services.
* Preserve evidence/source IDs.
* Every hypothesis must reference evidence.
* Request more evidence when insufficient.

### Diagnostic constraints

* Every factual claim must reference supplied evidence.
* Prefer temporal correlation and multiple independent signals.
* High confidence requires multiple independent evidence signals.
* Do not invent remediation commands.
* Recommend only existing approved runbooks.
* Require human review when evidence is insufficient.

### Remediation constraints

* Only approved safe/reversible procedures.
* Production changes require human approval.
* Destructive actions are blocked.
* No unrestricted infrastructure execution.

### RCA constraints

* Blameless analysis.
* Facts and hypotheses are separated.
* Evidence IDs are preserved.
* No fabricated timestamps or system states.
* Prevention recommendations are clearly marked.

---

# 🔍 Hallucination & Groundedness Controls

SentinelOps applies multiple controls:

```text
Evidence IDs
     ↓
Structured Agent Outputs
     ↓
Role-specific Constraints
     ↓
Deterministic Retrieval
     ↓
Safety Policy
     ↓
Human Approval
```

The goal is not simply to make the model produce an answer.

The goal is to make the answer:

**traceable → constrained → reviewable → governable**

---

# 📊 Observability & Audit Trail

Every incident produces an auditable decision path:

```text
ALERT_INGEST
      ↓
TRIAGE
      ↓
EVIDENCE_RETRIEVAL
      ↓
DIAGNOSIS
      ↓
SAFETY_GATE
      ↓
HITL
      ↓
REMEDIATION
      ↓
RCA
```

The dashboard exposes the decision state directly so an SRE can understand what the system did and why.

---

# 📋 Automated Post-Mortem

The RCA Agent produces a blameless incident report containing:

* Incident title
* Impact
* Root cause
* Evidence
* Timeline
* Remediation
* Prevention recommendations

The RCA stage prevents incident analysis from ending when the immediate remediation decision is made.

---

# 🖥️ SRE Incident Command Center

The web interface provides a single incident view containing:

* P1 severity
* Error rate
* Memory utilization
* End-to-end latency
* Root cause
* Confidence
* Evidence chain
* Alternative hypotheses
* Safety gate
* Blocked actions
* Recommended remediation
* HITL controls
* Retrieval results
* Context reduction
* Audit timeline
* Lyzr execution mode

### Live execution indicator

```text
EXECUTION MODE

LYZR LIVE

Triage → Diagnosis → Remediation → RCA
```

---

# 🛠️ Technology Stack

### AI / Agents

* Lyzr Agent Lab
* Lyzr Agent API
* GPT-based specialized agents

### Backend

* Python
* FastAPI
* Requests

### Frontend

* HTML
* CSS
* JavaScript

### Infrastructure

* Docker
* Render

### Data

* Synthetic Prometheus/Kubernetes-style telemetry
* Mock incident history
* Deterministic evidence retrieval
* Approved remediation/runbook metadata

---

# 📁 Repository Structure

```text
sentinelops-ai/
│
├── agents/
│   ├── README.md
│   ├── triage_agent.txt
│   ├── diagnostic_agent.txt
│   ├── remediation_agent.txt
│   └── rca_agent.txt
│
├── backend/
│   ├── main.py
│   ├── lyzr_client.py
│   ├── retrieval.py
│   ├── safety.py
│   ├── telemetry.py
│   └── requirements.txt
│
├── data/
│   └── runbooks/
│
├── frontend/
│   └── index.html
│
├── tests/
│   └── test_safety.py
│
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

# ⚙️ Local Setup

## 1. Clone

```bash
git clone https://github.com/thenmalar-13/sentinelops-ai.git
cd sentinelops-ai
```

## 2. Create environment

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r backend/requirements.txt
```

## 4. Configure environment

Copy:

```text
.env.example
```

to:

```text
.env
```

Configure the Lyzr credentials and agent IDs.

**Never commit real API keys.**

## 5. Run

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Open:

```text
http://localhost:8000
```

---

# 🐳 Docker

```bash
docker build -t sentinelops-ai .
docker run -p 8000:8000 sentinelops-ai
```

---

# 🔐 Security Notes

The MVP intentionally does **not** connect to a real production Kubernetes cluster.

The remediation endpoint is simulated.

Production credentials, API keys, and infrastructure access are not included in the repository.

The architecture is designed so that real execution can be introduced later behind:

* authentication,
* authorization,
* runbook allowlists,
* approval workflows,
* audit logging,
* sandbox validation,
* Kubernetes RBAC,
* rollback verification.

---

# 🧪 Safety Testing

Safety logic can be tested with:

```bash
pytest tests/
```

The safety layer verifies that destructive operations are rejected and that production-changing remediation requires human approval.

---

# 🏆 Rubric Alignment

| Evaluation Area                 | SentinelOps AI                                                           |
| ------------------------------- | ------------------------------------------------------------------------ |
| **Lyzr Agent Orchestration**    | Four specialized Lyzr agents connected through a governed pipeline       |
| **DevOps Safety & Reliability** | Safety gate, destructive-action blocking, approved remediation, HITL     |
| **Code Quality**                | Modular FastAPI backend, separated retrieval/safety/Lyzr client layers   |
| **SRE UX**                      | Incident Command Center with diagnosis, evidence, safety and audit state |
| **Hallucination Mitigation**    | Evidence-only reasoning + constrained prompts + structured outputs       |
| **Groundedness**                | Evidence IDs attached to diagnostic reasoning                            |
| **Retrieval Quality**           | Relevant telemetry/log/deployment evidence selected before diagnosis     |
| **Cost / Token Optimization**   | Demonstrated 92% context reduction                                       |
| **Prompt Architecture**         | Specialized role, safety and evidence constraints per agent              |
| **Latency Optimization**        | Context reduction and focused agent responsibilities                     |

---

# 🚀 Future Extensions

The architecture can be extended toward:

### Live Kubernetes Sandbox

Connect to Kind/Minikube for controlled non-destructive workflows.

### Voice Incident Briefing

Provide spoken incident summaries for on-call engineers.

### AIMS Decision Graph

Persist diagnostic reasoning and decision relationships.

### Production Integrations

Integrate with:

* PagerDuty
* Prometheus
* Datadog
* CloudWatch
* Kubernetes
* OpenTelemetry

All production integrations would remain behind authentication, authorization, safety policy and HITL controls.

---

# 🎥 Demo Flow

The recommended judge demo is:

```text
1. Open Live Demo
        ↓
2. Analyze P1 Incident
        ↓
3. Show 18.7% error rate + 94% memory
        ↓
4. Show 95% evidence-grounded diagnosis
        ↓
5. Show evidence chain
        ↓
6. Show 92% context reduction
        ↓
7. Show HITL_REQUIRED
        ↓
8. Show blocked destructive actions
        ↓
9. Show rollback recommendation
        ↓
10. Show LYZR LIVE
        ↓
11. Show Triage → Diagnosis → Remediation → RCA
```

---

# 🌐 Links

### Live Application

**https://sentinelops-ai-3.onrender.com**

### Source Code

**https://github.com/thenmalar-13/sentinelops-ai**

---

# 👩‍💻 Built for HiDevs Agent Arena — PS 03

**Enterprise Cloud Incident Triage & Runbook Remediation Agent**

SentinelOps AI demonstrates how specialized AI agents can assist SRE teams while preserving:

> **Evidence → Governance → Human Control → Auditability**

---

## ⚠️ MVP Disclaimer

This project uses synthetic Prometheus/Kubernetes-style incident data and simulated remediation execution for safe demonstration.

**No real production infrastructure is modified by the MVP.**

````

### Why this README is stronger

The important thing is that a judge can open your repository and understand the whole project **without having to run it first**.

It explicitly answers the four PS03 scoring questions:

**"Where is Lyzr?"** → four named Lyzr agents + live API.

**"Where is safety?"** → blocked destructive operations + HITL.

**"Where is the intelligence?"** → retrieval + evidence IDs + diagnosis.

**"Where is the engineering?"** → modular backend + frontend + safety + tests + Docker.

And importantly, it doesn't pretend that your simulated Kubernetes environment is a real production cluster. That honesty will help rather than hurt you.

---

# 2. About screenshots/videos on HiDevs

From the challenge page you pasted, the current flow is:

**Connect repo → feedback → submit → evaluation → rewards**

and the page specifically says:

> **"Submit for Dr Agent feedback"**

The page also says the **same repo you select will be used for review**.

I can't see the authenticated submission form itself because the public page redirects to login, so **don't upload anything randomly yet**.

### Do this now:

On your HiDevs challenge page:

**Scroll to `Submit for Dr Agent feedback` → click it.**

That should take you into the submission/review flow.

### If it asks for links

Use:

**GitHub Repository**
[thenmalar-13/sentinelops-ai](https://github.com/thenmalar-13/sentinelops-ai?utm_source=chatgpt.com)

**Live Demo**
[SentinelOps AI Live Demo](https://sentinelops-ai-3.onrender.com?utm_source=chatgpt.com)

### If it asks for screenshots

Use these **3**, in this order:

**Screenshot 1 — Overall result**
- P1
- 18.7% error
- 94% memory
- root cause
- 95% confidence

**Screenshot 2 — Safety**
- `HITL_REQUIRED`
- blocked `DROP DATABASE`
- blocked `DELETE POD`
- blocked `REBOOT CLUSTER`
- rollback recommendation

**Screenshot 3 — Architecture/optimization**
- retrieval evidence
- 92% context reduction
- audit timeline
- `LYZR LIVE`

### If it asks for a demo video

Record **2 minutes maximum**.

Don't record yourself explaining the code.

Record the **actual live application** and follow this sequence:

> **"This is SentinelOps AI, a governed multi-agent SRE incident response system."**

Then:

**Analyze P1 Incident**

> "A synthetic checkout-api incident is showing an 18.7% error rate and 94% memory utilization."

Show diagnosis.

> "The Lyzr Diagnostic Agent correlates deployment DEP-4821 with memory growth and repeated memory-pressure restarts. The diagnosis is 95% confident and grounded in the displayed evidence."

Scroll down.

> "Before remediation, the safety gate blocks destructive operations and requires explicit human approval."

Show:

`HITL_REQUIRED`

Then:

> "The recommended action is a low-risk rollback to the previous known-good version."

Finally show:

`LYZR LIVE`

> "The complete pipeline is orchestrated through four specialized Lyzr agents: Triage, Diagnosis, Remediation and RCA."

**Stop.**

That's much stronger than a long 7–10 minute walkthrough.

---

# 3. One VERY important thing before you submit

Because your repo is what the HiDevs evaluator will inspect, **commit the README first**.

Then check GitHub visually.

You want the repository homepage to immediately show:

```text
SentinelOps AI
↓
Live Demo
↓
What it solves
↓
Architecture
↓
Lyzr agents
↓
Safety/HITL
↓
Evidence grounding
↓
92% context reduction
↓
Rubric alignment
↓
Setup
````

Then click **Submit for Dr Agent feedback**.

## And bro — don't submit blindly.

**Send me a screenshot of the page that opens after you click `Submit for Dr Agent feedback`.**

I'll tell you **exactly what to put in every submission field**, including what to upload/link for screenshots, demo video, description, and any judge-facing answers. That is the last step where we can optimize your presentation before the **10 PM evaluation**. 🏆🔥
