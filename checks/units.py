import re
from collections import Counter
from typing import List

from core.models import Alert
from utils.normalize import try_parse_number


def check_units(source: str, target: str, units: List[str]) -> List[Alert]:
    alerts: List[Alert] = []
    if not units:
        return alerts

    units_escaped = sorted([re.escape(u) for u in units], key=len, reverse=True)
    unit_re = re.compile(rf"([+-]?\d[\d\s.,\u00A0]*)(?:\s*)({'|'.join(units_escaped)})\b")

    src = []
    tgt = []

    for m in unit_re.finditer(source):
        n = try_parse_number(m.group(1))
        u = m.group(2)
        if n is not None:
            src.append((n, u))

    for m in unit_re.finditer(target):
        n = try_parse_number(m.group(1))
        u = m.group(2)
        if n is not None:
            tgt.append((n, u))

    src_counter = Counter(src)
    tgt_counter = Counter(tgt)

    for key, c in src_counter.items():
        if tgt_counter[key] < c:
            n, u = key
            alerts.append(Alert(
                severity="Warning",
                check="Units",
                source_evidence=f"{n} {u}",
                target_evidence="(em falta ou diferente)",
                message="Valor com unidade do original não foi encontrado na tradução.",
                suggestion="Confirmar se a unidade foi omitida/trocada (ex.: mg↔g, cm↔mm)."
            ))

    return alerts