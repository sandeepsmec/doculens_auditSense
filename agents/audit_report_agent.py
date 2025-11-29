# agents/audit_report_agent.py

from crewai import Agent, Task

# --- Audit Report Generator Agent ---

audit_report_agent = Agent(
    role="Audit Report Generator",
    goal=(
        "Take compliance control evaluations and produce a complete audit readiness "
        "report including scores, gaps, domain summaries, and actionable recommendations."
    ),
    backstory=(
        "You are a senior compliance auditor. You convert raw control evaluations "
        "into clear, structured audit reports. You think in terms of readiness scores, "
        "domains, gaps, risks, and practical next steps."
    ),
    tools=[],          # LLM-only agent
    llm=None,          # Crew will inject the LLM via chat_llm
    verbose=True,
)

# --- Task ---

audit_report_task = Task(
    name="Generate Audit Readiness Report",
    description=(
        "Input:\n"
        "- standard_name: {standard_name}\n"
        "- scope: {scope}\n"
        "- evaluations: {evaluations}\n\n"
        "Task:\n"
        "Using the provided control evaluations, generate a structured audit readiness report.\n"
        "For each evaluation, coverage will be 'covered', 'partially_covered', or 'not_covered'.\n"
        "You must:\n"
        "1. Compute an overall readiness score between 0 and 1.\n"
        "   - covered = 1\n"
        "   - partially_covered = 0.5\n"
        "   - not_covered = 0\n"
        "2. Group controls by their domain (if present) and compute per-domain scores.\n"
        "3. Identify key gaps: the most important missing or weak controls.\n"
        "4. Produce 3–7 global recommendations to improve readiness.\n"
        "5. Return a final structured dict:\n\n"
        "{\n"
        "  'standard_name': '...',\n"
        "  'scope': '...',\n"
        "  'overall_readiness': 0.72,\n"
        "  'overall_summary': '... short human-readable summary ...',\n"
        "  'domain_scores': [\n"
        "       {\n"
        "         'domain': 'A.5',\n"
        "         'score': 0.66,\n"
        "         'covered': 3,\n"
        "         'partial': 1,\n"
        "         'missing': 1,\n"
        "         'key_gaps': ['missing management approval', 'policy not communicated']\n"
        "       }\n"
        "  ],\n"
        "  'evaluations': [... copy input evaluations, unchanged ...],\n"
        "  'global_recommendations': ['...', '...', '...']\n"
        "}\n"
    ),
    expected_output=(
        "A Python dict with keys: standard_name, scope, overall_readiness, overall_summary, "
        "domain_scores, evaluations, global_recommendations."
    ),
    agent=audit_report_agent,
)
