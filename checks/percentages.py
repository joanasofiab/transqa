import re
from collections import Counter
from typing import List

from core.models import Alert
from utils.normalize import try_parse_number

PCT_RE = re.compile(r"([+-]?\d+(?:[.,]\d+)?)\s*%")

def check_percentages(source: str, target: str) -> List[Alert]:
    alerts: List[Alert] = []

    src_vals = [try_parse_number(m.group(1)) for m in PCT_RE.finditer(source)]
    tgt_vals = [try_parse_number(m.group(1)) for m in PCT_RE.finditer(target)]

    src_vals = [x for x in src_vals if x is not None]
    tgt_vals = [x for x in tgt_vals if x is not None]

    src_counter = Counter(src_vals)
    tgt_counter = Counter(tgt_vals)

    for v, c in src_counter.items():
        if tgt_counter[v] < c:
            alerts.append(Alert(
                severity="Critical",
                check="Percentages",
                source_evidence=f"{v}%",
                target_evidence="(em falta ou diferente)",
                message="Percentagem do original não foi encontrada na tradução.",
                suggestion="Confirmar se o valor e o símbolo % foram preservados."
            ))

    if src_vals and not tgt_vals:
        alerts.append(Alert(
            severity="Critical",
            check="Percentages",
            source_evidence="(percentagens presentes)",
            target_evidence="(0 detetadas)",
            message="O original contém percentagens, mas nenhuma foi detetada na tradução.",
            suggestion="Verificar se o símbolo % foi removido."
        ))

    return alerts