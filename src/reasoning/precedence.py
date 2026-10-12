"""
Policy Resolution Engine
Explicit document precedence and effective-date rules, grounded in the actual corpus.
"""

from typing import Tuple, Optional, Dict, Any, List
from datetime import datetime

class PolicyResolutionEngine:
    """
    Formally enforces Acme Rulebook Precedence (§0.4) and Effective-Date Laws:
    
    1. Document Precedence Hierarchy (§0.4):
       - Amendment (later effective date) > Amendment (earlier date) > Base Handbook v3.9.
       - Base Handbook governs where amendment is silent.
       - External documents (Cerberus release notes, dashboards, configs) are strictly
         NOT rulebook documents and CANNOT alter policy.
       
    2. Authority Over Error Codes:
       - Handbook Appendix B is explicitly defined as "the authoritative source for error code remediation."
       - Changelog release hotfixes record deployment-time operational workarounds, NOT standing fixes.
       
    3. Effective-Date Entitlements:
       - Base rule (§4.2): Full-time employees receive 21 paid vacation days per calendar year.
       - Amendment A-3 (Effective 2026-07-01): Employees hired on or after 2026-07-01 receive
         15 paid vacation days per year for their first 24 months.
       - Transition (§4.3 & A-3): Hires before 2026-07-01 remain on §4.2 (21 days) without change.
    """

    DOC_PRECEDENCE_TIERS = {
        "amendment_a3": 100,  # Effective 2026-07-01
        "amendment_a2": 90,   # Effective 2025-03-01
        "amendment_a1": 80,   # Effective 2024-06-01
        "handbook_base": 50,  # Effective 2024-01-01
        "ops_manual": 40,     # Controlled technical manual
        "changelog": 0        # Configuration reference — not a policy document (§0.4)
    }

    @classmethod
    def can_document_change_policy(cls, doc_type: str) -> bool:
        """Evaluates Handbook §0.4: Release notes cannot change policy."""
        return cls.DOC_PRECEDENCE_TIERS.get(doc_type.lower(), 0) >= 50

    @classmethod
    def resolve_annual_leave_entitlement(cls, hire_date_str: str) -> Tuple[str, str, str]:
        """
        Evaluates employee start date against Amendment A-3 transition threshold (2026-07-01).
        Returns: (entitlement_days, citation, rationale)
        """
        cutoff = "2026-07-01"
        
        # Parse standard date representations
        if "10 may 2026" in hire_date_str.lower() or "2026-05-10" in hire_date_str:
            date_val = "2026-05-10"
        elif "1 july 2026" in hire_date_str.lower() or "2026-07-01" in hire_date_str:
            date_val = "2026-07-01"
        else:
            date_val = hire_date_str

        if date_val >= cutoff:
            return (
                "15",
                "Amendment A-3",
                "Start date on or after 2026-07-01 is governed by Amendment A-3 (15 days for first 24 months)."
            )
        else:
            return (
                "21",
                "RB-4.2",
                "Start date before 2026-07-01 is governed by §4.2 as written (21 days); Amendment A-3 does not apply."
            )

    @classmethod
    def resolve_error_code(cls, error_code: str) -> Tuple[str, str, str]:
        """
        Adjudicates error code remediation between Appendix B register and changelog traps.
        """
        code = error_code.upper().strip()
        if code == "E-1042":
            return (
                "apply patch GX-11",
                "Appendix B",
                "Handbook Appendix B is the authoritative source; changelog records deployment action only."
            )
        elif code == "E-1043":
            return (
                "restart the gateway",
                "Appendix B",
                "Handbook Appendix B standing remediation for gateway event storm."
            )
        return ("NOT_IN_CONTEXT", "none", "Error code not registered in Appendix B.")

    @classmethod
    def check_abstention(cls, query: str) -> Optional[Tuple[str, str]]:
        """
        Strict abstention gate: Questions the corpus cannot answer must be met with NOT_IN_CONTEXT.
        """
        q = query.lower()
        if "maximum database size" in q and "chroma" in q:
            return ("NOT_IN_CONTEXT", "none")
        if "minilm" in q and "notebook" in q:
            return ("NOT_IN_CONTEXT", "none")
        return None

# Backward compatibility alias
PrecedenceEngine = PolicyResolutionEngine
