import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crewai import Crew
from agents.audit_doc_loader_agent import (
    audit_doc_loader_agent,
    audit_doc_loader_task
)

def test_audit_doc_loader_basic():
    # Input for the document loader
    inputs = {
        "source_url": "https://raw.githubusercontent.com/python/cpython/main/LICENSE",
        "doc_id": "test_doc"
    }

    # Create crew with ONLY the loader agent
    crew = Crew(
        agents=[audit_doc_loader_agent],
        tasks=[audit_doc_loader_task],
        chat_llm=None,      # no LLM needed
        manager_llm=None,
        planning_llm=None,
        function_calling_llm=None,
        verbose=True,
    )

    # Run it
    result = crew.kickoff(inputs=inputs)

    print("\n📄 AuditDocLoader Output:\n", result)

    # Basic assertions (safe for any text)
    # assert isinstance(result, dict)
    # assert "doc_id" in result
    # assert "document_text" in result
    # assert result["doc_id"] == "test_doc"
