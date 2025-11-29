# agents/standard_extractor_agent.py

from crewai import Agent, Task, LLM
from tools.fetch_document_tool import FetchDocumentTool

llm = LLM(model="openai/gpt-5-nano")

# --- Standard Extractor Agent ---

standard_extractor_agent = Agent(
    role="Compliance Standard & Control Extractor",
    goal=(
        "Fetch the compliance standard from the provided URL and extract a list of "
        "atomic compliance controls."
    ),
    backstory=(
        "You load standards such as ISO 27001, SOC2, GDPR, DPDP, and break them "
        "into small, auditor-friendly requirements."
    ),
    tools=[FetchDocumentTool()],   # <-- added
    verbose=True,
    llm=llm,
)

# --- Standard Extractor Task ---

standard_extractor_task = Task(
    name="Fetch and Extract Compliance Controls",
    description=(
        "Input:\n"
        "- `standard_name`: {standard_name}\n"
        "- `standard_url`: {standard_url}\n\n"

        "Task:\n"
        "1. Fetch the standard text from `standard_url` using your tool.\n"
        "2. Read the full text.\n"
        "3. Extract a list of atomic compliance controls.\n\n"

        "Each control MUST contain:\n"
        "- id (use real IDs if present, otherwise CTRL-001, CTRL-002...)\n"
        "- title\n"
        "- description\n"
        "- domain (optional)\n"
        "- priority (optional)\n\n"

        "Output:\n"
        "A Python list of dicts, e.g.:\n"
        "[\n"
        "  {\n"
        "    'id': 'A.5.1',\n"
        "    'title': 'Security Policy',\n"
        "    'description': '...',\n"
        "    'domain': 'A.5',\n"
        "    'priority': 'high'\n"
        "  }\n"
        "]"
    ),
    expected_output=(
        "A Python list of dicts: each dict has id, title, description, "
        "and optional domain and priority."
    ),
    agent=standard_extractor_agent,
)
