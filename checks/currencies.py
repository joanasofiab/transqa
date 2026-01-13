import re
from typing import List, Set, Tuple

from core.models import Alert
from utils.normalize import try_parse_number

def check_currencies(source: str, target: str, currency_symbols: List[str]) -> List[Alert]:
    alerts: List[Alert] = []

    sym = re.escape("".join(currency_symbols))
    cur_re = re.compile(rf"([{sym}])\s*([+-]?\d[\d\s.,\u00A0]*)")

    src_pairs: List[Tuple[str, object]] = []
    for m in cur_re.finditer(source):
        s = m.group(1)
        n = try_parse_number(m.group(2))
        if n is not None:
            src_pairs.append((s, n))

    tgt_set: Set[Tuple[str, object]] = set()
    for m in cur_re.finditer(target):
        s = m.group(1)
        n = try_parse_number(m.group(2))
        if n is not None:
            tgt_set.add((s, n))

    for s, n in src_pairs[:50]:
        if (s, n) not in tgt_set:
            alerts.append(Alert(
                severity="Critical",
                check="Currencies",
                source_evidence=f"{s}{n}",
                target_evidence="(em falta ou diferente)",
                message="Montante monetário do original não foi encontrado na tradução (símbolo+valor).",
                suggestion="Confirmar se o símbolo e o valor foram preservados."
            ))

    return alerts