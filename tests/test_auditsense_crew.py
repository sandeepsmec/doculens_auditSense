import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from crew_definition import AuditSenseCrew


def test_auditsense_full_pipeline():
    """
    End-to-end test:
      1. Standard Loader → Standard Extractor
      2. Evidence Loader (company doc)
      3. Evidence Mapper (controls ↔ documents)
      4. Audit Report Generator
    """

    # Instantiate the class-based crew (matches DocLensAI structure)
    crew = AuditSenseCrew()

    # ------------------------------------------------------------
    # 1) Standard document URL (host THIS after upload)
    # ------------------------------------------------------------
    standard_url = (
        "https://raw.githubusercontent.com/sandykwl/audit-sense-demo/refs/heads/main/demo/standards/nist_sp80053r5_abridged.txt"
    )

    # ------------------------------------------------------------
    # 2) Evidence document URL
    # ------------------------------------------------------------
    evidence_url = (
        "https://raw.githubusercontent.com/sandykwl/audit-sense-demo/refs/heads/main/demo/evidence/acmecorp_security_policy.txt"
    )

    # ------------------------------------------------------------
    # 3) Inputs to full AuditSense Pipeline
    # ------------------------------------------------------------
    inputs = {
        # Standard Extractor
        "standard_name": "NIST SP 800-53 Rev5 (Abridged)",
        "standard_url": standard_url,
        "standard_text": None,

        # Evidence Loader
        "source_url": evidence_url,
        "doc_id": "policy_doc",

        # Mapper
        "documents": None,
        "controls": None,

        # Audit Report
        "evaluations": None,
        "scope": "Full Pipeline Test - External Docs",
    }

    # ------------------------------------------------------------
    # 4) Execute pipeline (class-based requires .crew.kickoff)
    # ------------------------------------------------------------
    result = crew.crew.kickoff(inputs=inputs)

    print("\n🔎 Full AuditSense Pipeline Output:\n", result)

    # ------------------------------------------------------------
    # 5) Basic assertions (optional)
    # ------------------------------------------------------------
    # assert isinstance(result, dict)
    # assert "overall_readiness" in result
    # assert "global_recommendations" in result
    # assert "domain_scores" in result

    print("\n✅ AuditSense full pipeline test completed.\n")
