from dataclasses import dataclass

@dataclass
class Alert:
    severity: str
    check: str
    source_evidence: str
    target_evidence: str
    message: str
    suggestion: str