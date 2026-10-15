"""Conservative T-SQL feature scanner, with lexical masking for comments/strings.

This is an *assessment* tool, not a SQL parser or automatic translator.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import re


@dataclass(frozen=True)
class Rule:
    code: str
    severity: str
    pattern: str
    description: str
    migration_note: str


RULES = (
    Rule("TOP", "medium", r"\bTOP\s*(?:\(\s*[^)\n]+\s*\)|\d+)",
         "T-SQL TOP row limiter", "Use FETCH FIRST / OFFSET FETCH with deterministic ORDER BY; review WITH TIES and variables."),
    Rule("DATEADD", "medium", r"\bDATEADD\s*\(",
         "SQL Server date arithmetic", "Map each date part individually (e.g. ADD_MONTHS); check month-end behavior."),
    Rule("DATEDIFF", "high", r"\bDATEDIFF\s*\(",
         "SQL Server boundary-counting date difference", "Do not replace blindly with date subtraction: boundary semantics differ."),
    Rule("GETDATE", "low", r"\bGETDATE\s*\(\s*\)",
         "SQL Server server-local timestamp", "Choose CURRENT_TIMESTAMP, SYSTIMESTAMP, or SYSDATE based on type/time-zone requirements."),
    Rule("ISNULL", "medium", r"\bISNULL\s*\(",
         "SQL Server null replacement", "Review datatype/length rules; COALESCE and NVL are not always drop-in replacements."),
    Rule("IDENTITY", "high", r"\bIDENTITY\s*\(",
         "SQL Server identity column", "Choose Oracle identity or sequence + trigger; review existing key data and insert behavior."),
    Rule("SCOPE_IDENTITY", "high", r"\bSCOPE_IDENTITY\s*\(\s*\)",
         "Last identity key within SQL Server scope", "Prefer INSERT ... RETURNING ... INTO for Oracle; validate scope semantics."),
    Rule("OUTPUT_INSERTED", "high", r"\bOUTPUT\s+INSERTED\s*\.",
         "DML OUTPUT clause", "Evaluate Oracle RETURNING INTO or bulk DML patterns."),
    Rule("TABLE_VARIABLE", "high", r"\bDECLARE\s+@\w+\s+TABLE\s*\(",
         "SQL Server table variable", "Evaluate Oracle collection, GTT, or SQL type; compare transaction behavior."),
    Rule("TEMP_TABLE", "high", r"(?<!\w)#{1,2}[A-Za-z_]\w*",
         "SQL Server local/global temporary table", "Evaluate Oracle GLOBAL PRIVATE TEMPORARY TABLE availability and data lifecycle."),
    Rule("TRY_CATCH", "medium", r"\bBEGIN\s+(?:TRY|CATCH)\b",
         "T-SQL exception handling block", "Review PL/SQL EXCEPTION handling and transaction boundaries."),
    Rule("CROSS_APPLY", "medium", r"\b(?:CROSS|OUTER)\s+APPLY\b",
         "SQL Server APPLY operator", "Review LATERAL and OUTER APPLY support in target Oracle version."),
    Rule("BRACKET_IDENTIFIER", "low", r"\[(?:[^\]\n]|\]\])+\]",
         "SQL Server bracket-quoted identifier", "Use ordinary Oracle identifiers where possible; quoting changes case-sensitivity."),
    Rule("MERGE", "high", r"\bMERGE\s+(?:INTO\s+)?[A-Za-z_\[]",
         "Vendor-specific MERGE behavior", "Rewrite and test matched/unmatched branches, concurrency, and error behavior."),
    Rule("RAISERROR", "medium", r"\bRAISERROR\s*\(",
         "T-SQL error raising", "Use RAISE_APPLICATION_ERROR with explicit error mapping."),
)


def mask_non_code(source: str) -> str:
    """Preserve offsets/newlines; replace comments and literals with whitespace.

    Handles escaped single/double quotes and nested T-SQL block comments.
    The scanner intentionally does not claim full SQL grammar coverage.
    """
    result = list(source)
    i = 0
    length = len(source)

    def hide(pos: int) -> None:
        if source[pos] not in "\r\n":
            result[pos] = " "

    while i < length:
        if source.startswith("--", i):
            while i < length and source[i] not in "\r\n":
                hide(i)
                i += 1
        elif source.startswith("/*", i):
            depth = 0
            while i < length:
                if source.startswith("/*", i):
                    depth += 1
                    hide(i)
                    if i + 1 < length:
                        hide(i + 1)
                    i += 2
                elif source.startswith("*/", i):
                    depth -= 1
                    hide(i)
                    if i + 1 < length:
                        hide(i + 1)
                    i += 2
                    if depth == 0:
                        break
                else:
                    hide(i)
                    i += 1
        elif source[i] in ("'", '"'):
            quote = source[i]
            hide(i)
            i += 1
            while i < length:
                if source[i] == quote:
                    hide(i)
                    i += 1
                    if i < length and source[i] == quote:
                        hide(i)
                        i += 1
                    else:
                        break
                else:
                    hide(i)
                    i += 1
        else:
            i += 1
    return "".join(result)


def analyze_text(content: str, path: str = "<memory>") -> list[dict]:
    code = mask_non_code(content)
    findings: list[dict] = []
    for rule in RULES:
        for match in re.finditer(rule.pattern, code, flags=re.IGNORECASE):
            pos = match.start()
            last_newline = code.rfind("\n", 0, pos)
            finding = {
                "file": path,
                "line": code.count("\n", 0, pos) + 1,
                "column": pos - last_newline,
                "rule": rule.code,
                "severity": rule.severity,
                "description": rule.description,
                "guidance": rule.migration_note,
            }
            findings.append(finding)
    return sorted(findings, key=lambda x: (x["line"], x["column"], x["rule"]))


def assess(root: Path) -> dict:
    root = root.resolve()
    files = sorted([root] if root.is_file() and root.suffix.lower() == ".sql" else root.rglob("*.sql"))
    if not files:
        raise ValueError(f"No .sql files found in {root}")
    all_findings: list[dict] = []
    for file in files:
        rel = file.name if root.is_file() else file.relative_to(root).as_posix()
        all_findings.extend(analyze_text(file.read_text(encoding="utf-8-sig"), rel))
    counts = {severity: sum(f["severity"] == severity for f in all_findings)
              for severity in ("high", "medium", "low")}
    return {
        "assessment_type": "static_heuristic_not_compilation",
        "files_scanned": len(files),
        "finding_count": len(all_findings),
        "severity_counts": counts,
        "findings": all_findings,
    }


def to_markdown(report: dict) -> str:
    lines = ["# T-SQL Migration Assessment", "", "> Static heuristic assessment only. No SQL was executed or migrated.", "",
             f"Scanned files: **{report['files_scanned']}** · Findings: **{report['finding_count']}**", "",
             "| File | Line | Rule | Severity | Action |", "| --- | ---: | --- | --- | --- |"]
    for f in report["findings"]:
        lines.append(f"| `{f['file']}` | {f['line']} | `{f['rule']}` | {f['severity']} | {f['guidance']} |")
    return "\n".join(lines) + "\n"
