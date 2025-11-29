# agents/audit_doc_loader_agent.py

from crewai import Agent, Task
from tools.fetch_document_tool import FetchDocumentTool

# --- Document Loader Agent (Reader) ---

audit_doc_loader_agent = Agent(
    role="Audit Document Loader",
    goal=(
        "Fetch raw text from a given document source (URL or file). "
        "Do NOT analyze, evaluate, or summarize. Only extract plain text."
    ),
    backstory=(
        "You specialize in retrieving and extracting raw text from evidence "
        "documents used in compliance audits. You never interpret the content."
    ),
    tools=[FetchDocumentTool()],   # only fetch
    llm=None,                      # no LLM needed
    verbose=True,
)

# --- Document Loader Task ---

audit_doc_loader_task = Task(
    name="Load Evidence Document",
    description=(
        "Input:\n"
        "- `source_url`: {source_url}\n"
        "- `doc_id`: {doc_id}\n\n"
        "Output:\n"
        "Return a Python dict:\n"
        "{\n"
        "  'doc_id': doc_id,\n"
        "  'document_text': '...raw extracted text...'\n"
        "}\n"
    ),
    expected_output=(
        "A Python dict with keys: doc_id, document_text."
    ),
    agent=audit_doc_loader_agent,
)
