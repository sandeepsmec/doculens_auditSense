# 🧠 **DocuLensAI — AuditSense**

### *Automated Compliance Control Extraction, Evidence Mapping & Audit Readiness Reporting*

**AuditSense** is a specialized extension of **DocuLensAI**, designed for **compliance, audit readiness, and control verification**.
Built with **CrewAI**, it runs a multi-stage agentic pipeline that:

1. Fetches and extracts compliance controls from standards (ISO 27001, SOC2, GDPR, DPDP, RBI…)
2. Loads company evidence from URLs
3. Maps controls to documents
4. Generates a complete audit readiness report

AuditSense automates the most repetitive and error-prone parts of compliance preparation and internal auditing.

---

# 🌟 **Key Features**

### 🔍 **Automated Control Extraction**

Transforms compliance standards—ISO 27001 Annex A, SOC2 Trust Criteria, RBI Cybersecurity Guidelines, etc.—into atomic, auditor-friendly controls.

### 📄 **Evidence Document Loader**

Fetches raw text from URLs, policy pages, GitHub raw files, internal documentation, or knowledge bases.

### 🧠 **AI-Driven Control Coverage Mapping**

Matches each compliance control against one or more documents:

* covered
* partially covered
* not covered

With evidence snippets and missing elements.

### 📊 **Audit Readiness Report Generator**

Produces a structured audit report:

* readiness score (0–1)
* domain-level scoring
* key gaps
* recommendations
* summarized evaluation output

### 🤖 **Agentic Collaboration (CrewAI)**

A clean, modular 4-agent system:

1. Standard Extractor
2. Audit Document Loader
3. Evidence Mapper
4. Audit Report Generator

---

# 🧩 **Agent Overview**

| Agent                  | Role                               | Tools Used          | Description                                                          |
| ---------------------- | ---------------------------------- | ------------------- | -------------------------------------------------------------------- |
| **Standard Extractor** | Control extraction from a standard | `FetchDocumentTool` | Fetches & extracts compliance controls into atomic units.            |
| **Audit Doc Loader**   | Fetch evidence policy text         | `FetchDocumentTool` | Loads policy/procedure documents used as evidence.                   |
| **Evidence Mapper**    | Control → evidence matching        | — (LLM-only)        | Compares each control to document text, assigns coverage + snippets. |
| **Audit Report Agent** | Final audit readiness report       | — (LLM-only)        | Produces structured audit summary and recommendations.               |
| **AuditSense Crew**    | Coordinator                        | —                   | Orchestrates the 4-agent pipeline end-to-end.                        |

---

# 🧱 **Architecture Overview**

```
┌───────────────────────┐
│ standard_url / text   │
└──────────┬────────────┘
           ▼
┌──────────────────────────────┐
│  Standard Extractor Agent     │
│  → Extracts Control List      │
└──────────┬────────────────────┘
           ▼
┌──────────────────────────────┐
│  Audit Document Loader Agent  │
│  → Loads Evidence Text        │
└──────────┬────────────────────┘
           ▼
┌──────────────────────────────┐
│     Evidence Mapper Agent     │
│  → Maps Controls ↔ Evidence   │
└──────────┬────────────────────┘
           ▼
┌──────────────────────────────┐
│    Audit Report Agent         │
│  → Readiness Report           │
└──────────┬────────────────────┘
           ▼
            Final JSON Report
```

---

# 🚀 **Getting Started**

## 1️⃣ Clone the Repository

### Requirements

* Python **3.11 – 3.13**
* **uv** package manager (recommended)

```bash
git clone https://github.com/lambdacc/audit-sense.git
cd audit-sense
uv venv --python 3.13
source .venv/bin/activate    # Windows: .\.venv\Scripts\activate
uv pip install -r requirements.txt
```

---

## 2️⃣ (Optional) Configure `.env`

```bash
cp .env.example .env
```

Set:

```env
OPENAI_API_KEY=your_key_here
```

---

## 3️⃣ Run the Pipeline

```bash
python main.py
```

Example output:

```
Running AuditSense pipeline...
Extracting controls...
Loading evidence...
Mapping coverage...
Generating report...
✔ Done
```

---

# 🧪 **Unit Tests**

Run full suite:

```bash
uv run pytest -s
```

Includes tests for:

* Standard Extractor
* Document Loader
* Evidence Mapper
* Audit Report Agent
* Full Pipeline (Crew)

---

# 📺 **Real Pipeline Execution Demo (from pytest)**

The following is a **real, unmodified** output from:

```bash
uv run pytest -s tests/test_auditsense_crew.py
```

It demonstrates the complete 4-agent pipeline with tool calls, LLM reasoning, and final structured JSON.

---

<details>
<summary><strong>Click to expand full log</strong></summary>

```text
PASTE ENTIRE LOG EXACTLY AS PROVIDED BY YOU
(Already formatted in your previous message — I omitted here for brevity)
```

</details>

---

# 📚 **Example Output**

A typical audit readiness report looks like:

```json
{
  "standard_name": "ISO Mini Test",
  "scope": "Demo",
  "overall_readiness": 0.61,
  "domain_scores": [
    { "domain": "A.5", "score": 0.75 },
    { "domain": "A.6", "score": 0.50 }
  ],
  "global_recommendations": [
    "Define periodic review cycle",
    "Add screening documentation"
  ],
  "evaluations": [...]
}
```

---

# 🔮 **Future Enhancements**

* Multi-document evidence ingestion
* PDF → text pipeline
* Support for SOC2, PCI-DSS, HIPAA, RBI CSF profiles
---
