# crew_definition.py

from crewai import Crew, LLM
from logging_config import get_logger

from agents.standard_extractor_agent import (
    standard_extractor_agent,
    standard_extractor_task,
)
from agents.audit_doc_loader_agent import (
    audit_doc_loader_agent,
    audit_doc_loader_task,
)
from agents.evidence_mapper_agent import (
    evidence_mapper_agent,
    evidence_mapper_task,
)
from agents.audit_report_agent import (
    audit_report_agent,
    audit_report_task,
)


class AuditSenseCrew:
    """
    The full AuditSense multi-agent pipeline:
      1. Standard Extractor       → Extract compliance controls
      2. Audit Document Loader    → Load company evidence documents
      3. Evidence Mapper          → Map controls ↔ evidence text
      4. Audit Report Generator   → Produce readiness assessment output

    This matches the class-based structure used in DocuLensAI.
    """

    def __init__(self, verbose=True, logger=None):
        self.verbose = verbose
        self.logger = logger or get_logger(__name__)

        self.logger.info("Initializing AuditSenseCrew…")
        self.crew = self._create_crew()
        self.logger.info("AuditSenseCrew initialized successfully.")

    def _create_crew(self):
        """Assemble the multi-agent AuditSense pipeline."""

        self.logger.info("Creating agent pipeline…")

        llm = LLM(model="gpt-5-nano")

        crew = Crew(
            agents=[
                standard_extractor_agent,
                audit_doc_loader_agent,
                evidence_mapper_agent,
                audit_report_agent,
            ],
            tasks=[
                standard_extractor_task,
                audit_doc_loader_task,
                evidence_mapper_task,
                audit_report_task,
            ],
            chat_llm=llm,
            verbose=self.verbose,
        )

        self.logger.info("Crew assembly complete.")
        return crew
