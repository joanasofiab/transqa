import re
from typing import List, Tuple
from core.models import Alert

# DD/MM/YYYY ou DD-MM-YYYY
DMY_RE = re.compile(r"\b(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})\b")
# YYYY-MM-DD
YMD_RE = re.compile(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b")

def _is_ambiguous_dmy(d: int, m: int) -> bool:
    # Ambígua se d<=12 e m<=12 (03/04/2026)
    return d <= 12 and m <= 12

def _collect_dates(text: str) -> List[Tuple[str, bool]]:
    dates = []
    for m in DMY_RE.finditer(text):
        d = int(m.group(1)); mo = int(m.group(2))
        raw = m.group(0)
        dates.append((raw, _is_ambiguous_dmy(d, mo)))
    for m in YMD_RE.finditer(text):
        dates.append((m.group(0), False))
    return dates

def check_dates(source: str, target: str, warn_ambiguous: bool = True) -> List[Alert]:
    alerts: List[Alert] = []
    src_dates = _collect_dates(source)

    for raw, ambiguous in src_dates[:50]:
        if raw not in target:
            alerts.append(Alert(
                severity="Critical",
                check="Dates",
                source_evidence=raw,
                target_evidence="(não encontrado)",
                message="Data presente no original não foi encontrada na tradução.",
                suggestion="Confirmar se a data foi alterada ou reformulada; garantir equivalência."
            ))
        elif warn_ambiguous and ambiguous:
            alerts.append(Alert(
                severity="Warning",
                check="Dates",
                source_evidence=raw,
                target_evidence=raw,
                message="Data numérica potencialmente ambígua (DD/MM).",
                suggestion="Se possível, reescrever por extenso ou usar formato inequívoco."
            ))

    return alerts