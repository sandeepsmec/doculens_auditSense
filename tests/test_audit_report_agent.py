import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crewai import Crew, LLM
from agents.audit_report_agent import audit_report_agent, audit_report_task


def test_audit_report_agent_basic():
    # Sample input evaluations (normally comes from Evidence Mapper)
    evaluations = [
        {
            "control_id": "A.5.1",
            "coverage": "covered",
            "evidence": [
                {"doc_id": "policy.txt", "snippet": "We maintain security policies.", "score": 0.92}
            ],
            "missing_elements": [],
            "notes": "Fully satisfied."
        },
        {
            "control_id": "A.6.1",
            "coverage": "partially_covered",
            "evidence": [
                {"doc_id": "policy.txt", "snippet": "Roles are defined.", "score": 0.75}
            ],
            "missing_elements": ["No mention of periodic review"],
            "notes": "Needs improvement."
        },
        {
            "control_id": "A.7.1",
            "coverage": "not_covered",
            "evidence": [],
            "missing_elements": ["Employee screening procedures missing"],
            "notes": "No relevant content found."
        }
    ]

    inputs = {
        "standard_name": "ISO 27001 Annex A",
        "scope": "Basic sample test",
        "evaluations": evaluations
    }

    # Create Crew with LLM (required)
    llm = LLM(model="gpt-4o-mini")  # fast & cheap
    crew = Crew(
        agents=[audit_report_agent],
        tasks=[audit_report_task],
        chat_llm=llm,
        verbose=True,
    )

    # Run agent
    result = crew.kickoff(inputs=inputs)

    print("\n📝 Audit Report Agent Output:\n", result)

    # Basic sanity checks
    # assert isinstance(result, dict)
    # assert "overall_readiness" in result
    # assert "domain_scores" in result
    # assert "overall_summary" in result
    # assert "global_recommendations" in result
