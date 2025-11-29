# agents/evidence_mapper_agent.py

from crewai import Agent, Task

# --- Evidence Mapper Agent ---

evidence_mapper_agent = Agent(
    role="Evidence Mapper",
    goal=(
        "Compare extracted compliance controls with evidence documents and determine "
        "coverage, evidence snippets, missing elements, and auditor-style notes."
    ),
    backstory=(
        "You are an experienced compliance auditor. You match each control against "
        "the provided documents, extract supporting evidence, and identify gaps."
    ),
    tools=[],          # LLM only
    llm=None,          # LLM provided by Crew via chat_llm
    verbose=True,
)

# --- Evidence Mapper Task ---

evidence_mapper_task = Task(
    name="Map Evidence to Controls",
    description=(
        "Input:\n"
        "- controls: {controls}\n"
        "- documents: {documents}\n\n"

        "Task:\n"
        "For EACH control in `controls`, search across ALL documents and determine:\n\n"
        "1. coverage: one of 'covered', 'partially_covered', 'not_covered'\n"
        "2. evidence: list of dicts like:\n"
        "   { 'doc_id': '...', 'snippet': '...', 'score': 0-1 }\n"
        "3. missing_elements: a list of specific requirements not found\n"
        "4. notes: short auditor-style reasoning\n\n"

        "Output:\n"
        "A Python list of dicts, e.g.:\n\n"
        "[\n"
        "  {\n"
        "    'control_id': 'A.5.1',\n"
        "    'coverage': 'partially_covered',\n"
        "    'evidence': [\n"
        "      { 'doc_id': 'policy.txt', 'snippet': '...', 'score': 0.82 }\n"
        "    ],\n"
        "    'missing_elements': ['no annual review cycle'],\n"
        "    'notes': 'Some coverage exists but incomplete.'\n"
        "  }\n"
        "]"
    ),
    expected_output=(
        "A Python list of dicts. Each dict represents a control evaluation with keys: "
        "control_id, coverage, evidence, missing_elements, notes."
    ),
    agent=evidence_mapper_agent,
)
