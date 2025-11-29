import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crewai import Crew, LLM
from agents.standard_extractor_agent import (
    standard_extractor_agent,
    standard_extractor_task
)


def test_standard_extractor_agent():
    # A small test standard hosted as raw text
    standard_url = "https://raw.githubusercontent.com/github/gitignore/main/LICENSE"
    # Replace with your own mini-standard later

    inputs = {
        "standard_name": "ISO Mini Test",
        "standard_url": standard_url,
    }

    llm = LLM(model="gpt-4o-mini")

    crew = Crew(
        agents=[standard_extractor_agent],
        tasks=[standard_extractor_task],
        chat_llm=llm,
        verbose=True,
    )

    result = crew.kickoff(inputs=inputs)

    print("\n📝 Standard Extractor Output:\n", result)

    # Basic checks
    # assert isinstance(result, list)
    # assert len(result) > 0
    # assert "id" in result[0]
    # assert "title" in result[0]
    # assert "description" in result[0]
