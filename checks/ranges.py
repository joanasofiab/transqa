import re
from typing import List

from core.models import Alert

RANGE_RE = re.compile(r"\b(\d+(?:[.,]\d+)?)\s*[-–]\s*(\d+(?:[.,]\d+)?)\b")

def check_ranges(source: str, target: str) -> List[Alert]:
    alerts: List[Alert] = []
    src_ranges = [m.group(0) for m in RANGE_RE.finditer(source)]

    for r in src_ranges[:50]:
        if r not in target:
            alerts.append(Alert(
                severity="Warning",
                check="Ranges",
                source_evidence=r,
                target_evidence="(não encontrado)",
                message="Intervalo numérico do original não foi encontrado na tradução.",
                suggestion="Confirmar se o intervalo foi reescrito ou alterado."
            ))
    return alerts