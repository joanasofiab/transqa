import re
from collections import Counter
from typing import List, Tuple

from core.models import Alert

# Padrões típicos em localization/CAT:
# - chaves estilo {name}, {0}, {{literal}}
# - printf style: %s, %d, %.2f
# - tags: <b>, </a>, <br/>
# - escapes comuns: \n, \t
CURLY_RE = re.compile(r"(\{\{.*?\}\}|\{[^{}\s]+\})")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[+#\- 0]*(?:\d+)?(?:\.\d+)?[a-zA-Z]")
TAG_RE = re.compile(r"</?[a-zA-Z][^>]*?>")
ESC_RE = re.compile(r"\\[ntr]")

def _collect_tokens(text: str) -> List[Tuple[str, str]]:
    tokens: List[Tuple[str, str]] = []

    for m in CURLY_RE.finditer(text):
        tokens.append(("Curly", m.group(0)))

    for m in PRINTF_RE.finditer(text):
        tokens.append(("Printf", m.group(0)))

    for m in TAG_RE.finditer(text):
        tokens.append(("Tag", m.group(0)))

    for m in ESC_RE.finditer(text):
        tokens.append(("Escape", m.group(0)))

    return tokens


def check_placeholders(source: str, target: str, allow_reorder: bool = True) -> List[Alert]:
    """
    Verifica preservação de placeholders e tokens não-traduzíveis comuns em localization.

    allow_reorder:
      - True: exige que os tokens existam (não exige ordem)
      - False: exige sequência igual (útil em cenários estritos)
    """
    alerts: List[Alert] = []

    src_tokens = _collect_tokens(source)
    if not src_tokens:
        return alerts

    tgt_tokens = _collect_tokens(target)

    # modo estrito: compara listas (sequência)
    if not allow_reorder:
        src_list = [t for _, t in src_tokens]
        tgt_list = [t for _, t in tgt_tokens]
        if src_list != tgt_list:
            alerts.append(Alert(
                severity="Critical",
                check="Placeholders",
                source_evidence=" | ".join(src_list[:20]),
                target_evidence=" | ".join(tgt_list[:20]) if tgt_list else "(nenhum)",
                message="Sequência de placeholders/tokens difere entre original e tradução.",
                suggestion="Confirmar se todos os placeholders e tags foram preservados e na ordem correta."
            ))
        return alerts

    # modo flexível: compara contagens por token
    src_counter = Counter([tok for _, tok in src_tokens])
    tgt_counter = Counter([tok for _, tok in tgt_tokens])

    missing = []
    for tok, c in src_counter.items():
        if tgt_counter[tok] < c:
            missing.append(tok)

    if missing:
        sample = " | ".join(missing[:15])
        alerts.append(Alert(
            severity="Critical",
            check="Placeholders",
            source_evidence=sample,
            target_evidence="(em falta ou diferente)",
            message="Um ou mais placeholders/tokens do original não foram encontrados na tradução.",
            suggestion="Preservar exatamente placeholders (ex.: {name}, %s), tags HTML e escapes (ex.: \\n)."
        ))

    return alerts