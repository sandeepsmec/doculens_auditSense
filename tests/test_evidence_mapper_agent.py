import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crewai import Crew, LLM
from agents.evidence_mapper_agent import (
    evidence_mapper_agent,
    evidence_mapper_task
)


def test_evidence_mapper_basic():
    # Sample controls (normally produced by Standard Extractor)
    controls = [
        {
            "id": "A.5.1",
            "title": "Security Policy",
            "description": "The organization shall define, approve, and communicate an information security policy.",
            "domain": "A.5",
            "priority": "high"
        },
        {
            "id": "A.6.1",
            "title": "Roles and Responsibilities",
            "description": "Security roles and responsibilities shall be clearly defined and assigned.",
            "domain": "A.6",
            "priority": "medium"
        }
    ]

    # Sample document content (normally loaded from URL)
    documents = {
        "policy_doc": """
            Our evidence maintains an information security policy approved by management.
            Roles and responsibilities are assigned to the IT and security teams.
            No mention is made of periodic review or training requirements.
        """
    }

    inputs = {
        "controls": controls,
        "documents": documents
    }

    llm = LLM(model="gpt-4o-mini")

    crew = Crew(
        agents=[evidence_mapper_agent],
        tasks=[evidence_mapper_task],
        chat_llm=llm,
        verbose=True,
    )

    result = crew.kickoff(inputs=inputs)

    print("\n📝 Evidence Mapper Output:\n", result)

    # Basic assertions
    # assert isinstance(result, list)
    # assert len(result) == len(controls)
    # assert "control_id" in result[0]
    # assert "coverage" in result[0]
    # assert "evidence" in result[0]
