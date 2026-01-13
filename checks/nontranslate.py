import re
from typing import List
from core.models import Alert

URL_RE = re.compile(r"\bhttps?://[^\s<>()]+", re.IGNORECASE)
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
ID_RE = re.compile(r"\b[A-Z]{2,}-\d{2,}\b")  # ex: ABC-1234


def check_nontranslate(source: str, target: str) -> List[Alert]:
    alerts: List[Alert] = []

    src_urls = URL_RE.findall(source)
    src_emails = EMAIL_RE.findall(source)
    src_ids = ID_RE.findall(source)

    for u in src_urls:
        if u not in target:
            alerts.append(Alert(
                severity="Warning",
                check="Non-translate (URLs)",
                source_evidence=u,
                target_evidence="(não encontrado)",
                message="URL presente no original não foi encontrada na tradução.",
                suggestion="Confirmar se a URL deve manter-se exatamente igual."
            ))

    for e in src_emails:
        if e not in target:
            alerts.append(Alert(
                severity="Warning",
                check="Non-translate (Emails)",
                source_evidence=e,
                target_evidence="(não encontrado)",
                message="Email presente no original não foi encontrado na tradução.",
                suggestion="Confirmar se o email deve manter-se exatamente igual."
            ))

    for i in src_ids:
        if i not in target:
            alerts.append(Alert(
                severity="Warning",
                check="Non-translate (IDs)",
                source_evidence=i,
                target_evidence="(não encontrado)",
                message="Código/ID do original não foi encontrado na tradução.",
                suggestion="Confirmar se o identificador deve manter-se."
            ))

    return alerts