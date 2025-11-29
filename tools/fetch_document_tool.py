# agents/tools/fetch_document_tool.py

import requests
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


# ✅ Input schema for the tool
class FetchDocumentToolInput(BaseModel):
    source_url: str = Field(..., description="URL of the document to fetch")
    domain_keywords: str = Field(
        "", description="Comma-separated domain identifiers for downstream analysis"
    )


# ✅ Define the CrewAI BaseTool
class FetchDocumentTool(BaseTool):
    name: str = "Fetch Document Text from URL"
    description: str = (
        "Fetch plain text content from a URL. Returns raw document text and passes along "
        "domain keywords for downstream processing."
    )
    args_schema: Type[BaseModel] = FetchDocumentToolInput

    def _run(self, source_url: str, domain_keywords: str = "") -> dict:
        """Main tool logic: fetch text from the given URL with headers."""
        if not source_url:
            return {"document_text": None, "domain_keywords": domain_keywords, "error": "Missing source_url"}

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/118.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": source_url,
        }

        try:
            response = requests.get(source_url, headers=headers, timeout=15)
            response.raise_for_status()
            text = response.text

            return {
                "document_text": text,
                "domain_keywords": domain_keywords,
                "error": None,
            }

        except requests.exceptions.Timeout:
            return {"document_text": None, "domain_keywords": domain_keywords, "error": "Request timed out"}
        except requests.exceptions.RequestException as e:
            return {"document_text": None, "domain_keywords": domain_keywords, "error": f"HTTP error: {str(e)}"}
        except Exception as e:
            return {"document_text": None, "domain_keywords": domain_keywords, "error": f"Unexpected error: {str(e)}"}
