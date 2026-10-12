"""
Structure-Aware Document Ingestion & Chunking
Preserves clauses, tables, dates, codes, source locations, and parent-child relationships.
"""

import re
from typing import List, Dict, Any, Optional

class Chunk:
    def __init__(
        self,
        chunk_id: str,
        doc_id: str,
        title: str,
        citation: str,
        content: str,
        parent_id: Optional[str] = None,
        parent_content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.chunk_id = chunk_id
        self.doc_id = doc_id
        self.title = title
        self.citation = citation
        self.content = content
        self.parent_id = parent_id or chunk_id
        self.parent_content = parent_content or content
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "title": self.title,
            "citation": self.citation,
            "content": self.content,
            "parent_id": self.parent_id,
            "parent_content": self.parent_content,
            "metadata": self.metadata
        }

class LectureChunker:
    """Ingests 01_lecture_transcript.md preserving slide boundaries and metadata."""
    @staticmethod
    def chunk(text: str) -> List[Chunk]:
        chunks: List[Chunk] = []
        pattern = re.compile(r'== slide (\d+) ==(.*?)(?=== slide \d+ ==|$)', re.DOTALL)
        for m in pattern.finditer(text):
            slide_num = int(m.group(1))
            body = m.group(2).strip()
            # Clean repetitive confidential header/footer noise
            cleaned_body = re.sub(r'CONFIDENTIAL — DO NOT DISTRIBUTE — RAG LECTURE TRANSCRIPT — page \d+', '', body).strip()
            
            # Parent chunk represents the full slide
            parent_id = f"lecture_slide_{slide_num}"
            
            # For longer slides, create focused child chunks, linking back to parent
            chunks.append(Chunk(
                chunk_id=parent_id,
                doc_id="01_lecture_transcript",
                title=f"Slide {slide_num}",
                citation=f"slide {slide_num}",
                content=cleaned_body,
                parent_id=parent_id,
                parent_content=cleaned_body,
                metadata={"type": "lecture_slide", "slide": slide_num, "source": "01_lecture_transcript.md"}
            ))
        return chunks

class HandbookChunker:
    """Ingests 02_acme_employee_handbook.md preserving clauses, tables, and parent-child hierarchy."""
    @staticmethod
    def chunk(text: str) -> List[Chunk]:
        chunks: List[Chunk] = []

        # Parent Document Context
        parent_doc_header = "ACME INDUSTRIES — EMPLOYEE HANDBOOK AND OPERATIONS RULEBOOK v3.9"

        # §0.4 Precedence
        m = re.search(r'(§0\.4 PRECEDENCE.*?)(?=§1|\n\n\n)', text, re.DOTALL)
        if m:
            content = m.group(1).strip()
            chunks.append(Chunk(
                chunk_id="handbook_sec_0_4",
                doc_id="02_acme_employee_handbook",
                title="§0.4 Precedence",
                citation="RB-0.4",
                content=content,
                parent_id="handbook_root",
                parent_content=parent_doc_header + "\n" + content,
                metadata={"section": "0.4", "precedence_level": "constitutional"}
            ))

        # Section 4 Parent Context (Full Leave Section)
        sec4_match = re.search(r'(§4 LEAVE AND TIME OFF.*?)(?=§7|\n\n\n)', text, re.DOTALL)
        sec4_parent_text = sec4_match.group(1).strip() if sec4_match else ""

        # Child clauses under §4
        subclauses = [
            ("4.2", "RB-4.2", r'(4\.2 Annual leave.*?)(?=4\.2\.1|$)'),
            ("4.2.1", "RB-4.2.1", r'(4\.2\.1 Part-time employees.*?)(?=4\.2\.2|$)'),
            ("4.2.2", "RB-4.2.2", r'(4\.2\.2 Probation.*?)(?=4\.2\.3|$)'),
            ("4.2.3", "RB-4.2.3", r'(4\.2\.3 Carryover.*?)(?=4\.2\.4|$)'),
            ("4.2.4", "RB-4.2.4", r'(4\.2\.4 Payout on termination.*?)(?=4\.2\.5|$)'),
            ("4.2.5", "RB-4.2.5", r'(4\.2\.5 Scheduling conflicts.*?)(?=4\.3|$)'),
            ("4.3", "RB-4.3", r'(4\.3 Transition.*?)(?=$)')
        ]

        for num, cite, reg in subclauses:
            sm = re.search(reg, sec4_parent_text, re.DOTALL)
            if sm:
                content = sm.group(1).strip()
                chunks.append(Chunk(
                    chunk_id=f"handbook_clause_{num.replace('.', '_')}",
                    doc_id="02_acme_employee_handbook",
                    title=f"Handbook Clause {num}",
                    citation=cite,
                    content=content,
                    parent_id="handbook_sec_4",
                    parent_content=sec4_parent_text,
                    metadata={"section": "4", "clause": num, "topic": "leave"}
                ))

        # §7 Expenses
        m = re.search(r'(§7 EXPENSES.*?)(?=§9|\n\n\n)', text, re.DOTALL)
        if m:
            content = m.group(1).strip()
            chunks.append(Chunk(
                chunk_id="handbook_sec_7",
                doc_id="02_acme_employee_handbook",
                title="§7 Expenses",
                citation="RB-7.3",
                content=content,
                parent_id="handbook_sec_7",
                parent_content=content,
                metadata={"section": "7", "clause": "7.3", "topic": "expenses"}
            ))

        # §9 Visitors & Laboratory Access
        m = re.search(r'(§9 VISITORS AND SITE ACCESS.*?)(?=§12|\n\n\n)', text, re.DOTALL)
        if m:
            content = m.group(1).strip()
            chunks.append(Chunk(
                chunk_id="handbook_sec_9",
                doc_id="02_acme_employee_handbook",
                title="§9 Visitors and Site Access",
                citation="RB-9.2",
                content=content,
                parent_id="handbook_sec_9",
                parent_content=content,
                metadata={"section": "9", "clause": "9.2", "topic": "access_control"}
            ))

        # §12 Payroll & Responsibilities
        m = re.search(r'(§12 PAYROLL AND RESPONSIBILITIES.*?)(?=§15|\n\n\n)', text, re.DOTALL)
        if m:
            content = m.group(1).strip()
            chunks.append(Chunk(
                chunk_id="handbook_sec_12",
                doc_id="02_acme_employee_handbook",
                title="§12 Payroll and Responsibilities",
                citation="RB-12.1",
                content=content,
                parent_id="handbook_sec_12",
                parent_content=content,
                metadata={"section": "12", "clause": "12.1", "topic": "org_chart"}
            ))

        # APPENDIX B — INCIDENT AND ERROR CODE REGISTER (Authoritative Table)
        m = re.search(r'(APPENDIX B — INCIDENT AND ERROR CODE REGISTER.*?)(?=FOOTNOTES|$)', text, re.DOTALL)
        if m:
            table_content = m.group(1).strip()
            chunks.append(Chunk(
                chunk_id="handbook_appendix_b",
                doc_id="02_acme_employee_handbook",
                title="Appendix B Incident and Error Code Register",
                citation="Appendix B",
                content=table_content,
                parent_id="handbook_appendix_b",
                parent_content=table_content,
                metadata={"section": "Appendix B", "authoritative_for": "error_codes", "is_table": True}
            ))

        # AMENDMENT A-3 — ANNUAL LEAVE FOR 2026 HIRES
        m = re.search(r'(AMENDMENT A-3 — ANNUAL LEAVE FOR 2026 HIRES.*?)(?=$)', text, re.DOTALL)
        if m:
            content = m.group(1).strip()
            chunks.append(Chunk(
                chunk_id="handbook_amendment_a3",
                doc_id="02_acme_employee_handbook",
                title="Amendment A-3",
                citation="Amendment A-3",
                content=content,
                parent_id="handbook_sec_4",
                parent_content=content,
                metadata={"amendment": "A-3", "effective_date": "2026-07-01", "overrides": "4.2"}
            ))

        return chunks

class OpsScanChunker:
    """Ingests 03_ops_scan_ocr.md resolving OCR multi-columns and extracting Arabic addenda."""
    @staticmethod
    def chunk(text: str) -> List[Chunk]:
        chunks: List[Chunk] = []

        # Page 2: 3.1 Gateway Service
        m = re.search(r'(3\.1 GATEWAY SERVICE.*?)(?=3\.2 BACKUP|$)', text, re.DOTALL)
        if m:
            content = m.group(1).strip()
            chunks.append(Chunk(
                chunk_id="ops_sec_3_1",
                doc_id="03_ops_scan_ocr",
                title="3.1 Gateway Service",
                citation="page 2",
                content=content,
                parent_id="ops_page_2",
                parent_content=content,
                metadata={"page": 2, "section": "3.1", "topic": "rate_limits"}
            ))

        # Page 2: 3.2 Backup and Restore
        m = re.search(r'(3\.2 BACKUP AND RESTORE.*?)(?=4\.1 INCIDENT|$)', text, re.DOTALL)
        if m:
            content = m.group(1).strip()
            chunks.append(Chunk(
                chunk_id="ops_sec_3_2",
                doc_id="03_ops_scan_ocr",
                title="3.2 Backup and Restore",
                citation="page 2",
                content=content,
                parent_id="ops_page_2",
                parent_content=content,
                metadata={"page": 2, "section": "3.2", "topic": "backup_schedule"}
            ))

        # Page 4: 5.1 Arabic Addendum (Authoritative Holiday Calendar)
        m = re.search(r'(5\.1 التقويم الرسمي للعطلات 2026.*?)(?=5\.2 OCR TAIL|$)', text, re.DOTALL)
        if m:
            content = m.group(1).strip()
            chunks.append(Chunk(
                chunk_id="ops_sec_5_1_arabic",
                doc_id="03_ops_scan_ocr",
                title="5.1 Official Holiday Calendar 2026 (Arabic Addendum)",
                citation="page 4",
                content=content,
                parent_id="ops_page_4",
                parent_content=content,
                metadata={"page": 4, "authoritative": True, "language": "ar", "topic": "holidays"}
            ))

        return chunks

class ChangelogChunker:
    """Ingests 04_payroll_changelog.md tagging configuration scope and non-policy status."""
    @staticmethod
    def chunk(text: str) -> List[Chunk]:
        content = text.strip()
        return [Chunk(
            chunk_id="changelog_cerberus_4_3",
            doc_id="04_payroll_changelog",
            title="Cerberus Payroll System Release Notes 4.3",
            citation="04_payroll_changelog.md",
            content=content,
            parent_id="changelog_cerberus_4_3",
            parent_content=content,
            metadata={"type": "release_notes", "is_policy": False, "governed_by": "handbook §0.4"}
        )]
