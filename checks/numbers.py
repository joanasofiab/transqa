import re
from collections import Counter
from typing import List

from core.models import Alert
from utils.normalize import try_parse_number

# Números genéricos (evita apanhar números colados a letras)
NUM_RE = re.compile(
    r"(?<!\w)[+-]?\d{1,3}(?:[ .,\u00A0]\d{3})*(?:[.,]\d+)?(?!\w)|(?<!\w)[+-]?\d+(?:[.,]\d+)?(?!\w)"
)

# Padrões a remover antes do check de números (para evitar duplicação)
DMY_RE = re.compile(r"\b(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})\b")      # 03/04/2026
YMD_RE = re.compile(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b")              # 2026-04-03
RANGE_RE = re.compile(r"\b(\d+(?:[.,]\d+)?)\s*[-–]\s*(\d+(?:[.,]\d+)?)\b")  # 10–15
PCT_RE = re.compile(r"([+-]?\d+(?:[.,]\d+)?)\s*%")

# IDs do tipo ABC-1234 (para evitar FP em Numbers)
ID_RE = re.compile(r"\b[A-Z]{2,}-\d{2,}\b")


def _strip_covered_patterns(text: str, units: List[str], currency_symbols: List[str]) -> str:
    t = text

    # 0) remover IDs (ex.: ABC-1234), porque já são tratados pelo nontranslate
    t = ID_RE.sub(" ", t)

    # 1) datas
    t = DMY_RE.sub(" ", t)
    t = YMD_RE.sub(" ", t)

    # 2) intervalos
    t = RANGE_RE.sub(" ", t)

    # 3) percentagens
    t = PCT_RE.sub(" ", t)

    # 4) moedas (símbolo + número) — cobre €2500 e 2500€ também
    if currency_symbols:
        sym_chars = re.escape("".join(currency_symbols))
        sym_class = rf"[{sym_chars}]"
        num_pat = r"[+-]?\d[\d\s.,\u00A0]*"
        cur_re = re.compile(
            rf"(?:(?P<sym1>{sym_class})\s*(?P<num1>{num_pat})|(?P<num2>{num_pat})\s*(?P<sym2>{sym_class}))"
        )
        t = cur_re.sub(" ", t)

    # 5) unidades (número + unidade)
    if units:
        units_escaped = sorted([re.escape(u) for u in units], key=len, reverse=True)
        unit_re = re.compile(rf"([+-]?\d[\d\s.,\u00A0]*)(?:\s*)({'|'.join(units_escaped)})\b")
        t = unit_re.sub(" ", t)

    return t


def check_numbers(source: str, target: str, units: List[str], currency_symbols: List[str]) -> List[Alert]:
    alerts: List[Alert] = []

    src_clean = _strip_covered_patterns(source, units=units, currency_symbols=currency_symbols)
    tgt_clean = _strip_covered_patterns(target, units=units, currency_symbols=currency_symbols)

    src_raw = NUM_RE.findall(src_clean)
    tgt_raw = NUM_RE.findall(tgt_clean)

    src_nums = [try_parse_number(x) for x in src_raw]
    tgt_nums = [try_parse_number(x) for x in tgt_raw]

    src_nums = [x for x in src_nums if x is not None]
    tgt_nums = [x for x in tgt_nums if x is not None]

    src_counter = Counter(src_nums)
    tgt_counter = Counter(tgt_nums)

    for n, c in src_counter.items():
        if tgt_counter[n] < c:
            missing_count = c - tgt_counter[n]
            alerts.append(Alert(
                severity="Critical",
                check="Numbers",
                source_evidence=str(n),
                target_evidence="(em falta ou diferente)",
                message=f"Número do original não foi encontrado {missing_count}x na tradução (após normalização).",
                suggestion="Confirmar se o valor foi alterado ou se o formato numérico foi transformado incorretamente."
            ))

    return alerts