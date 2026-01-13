from typing import List
from core.models import Alert

PAIRS = [
    ("(", ")"),
    ("[", "]"),
    ("{", "}"),
    ("“", "”"),
    ('"', '"'),
]

def check_punctuation(source: str, target: str) -> List[Alert]:
    alerts: List[Alert] = []

    for left, right in PAIRS:
        s_bal = source.count(left) - source.count(right)
        t_bal = target.count(left) - target.count(right)

        if s_bal != t_bal:
            alerts.append(Alert(
                severity="Info",
                check="Punctuation",
                source_evidence=f"{left}…{right} (bal={s_bal})",
                target_evidence=f"{left}…{right} (bal={t_bal})",
                message="Diferença no balanceamento de pontuação/aspas entre original e tradução.",
                suggestion="Verificar se há parênteses/aspas abertos sem fecho (ou vice-versa)."
            ))

    return alerts