import re
from typing import Optional

# 1.200 / 12.345 / 1.234.567  -> milhares com ponto (PT/ES)
THOUSANDS_DOT_RE = re.compile(r"^[+-]?\d{1,3}(\.\d{3})+$")

# 1,200 / 12,345 / 1,234,567 -> milhares com vírgula (EN)
THOUSANDS_COMMA_RE = re.compile(r"^[+-]?\d{1,3}(,\d{3})+$")

# Número final já normalizado
SIMPLE_FLOAT_RE = re.compile(r"^[+-]?\d+(\.\d+)?$")

# Remove pontuação “de frase” no fim (muito comum em texto)
TRAILING_JUNK_RE = re.compile(r"[)\].,;:]+$")


def try_parse_number(s: str) -> Optional[float]:
    """
    Converte strings numéricas com formatações PT/EN/ES para float.
    Robusto a:
      - espaços e NBSP
      - pontuação final: "2,500." / "1200," / "(1200)" (parcialmente)
      - milhares PT/ES: 1.200 -> 1200
      - milhares EN: 2,500 -> 2500
      - decimal PT/ES: 12,5 -> 12.5
      - formatos com '.' e ',' simultaneamente:
          1.234,56 (PT/ES) e 1,234.56 (EN)
    """
    if s is None:
        return None

    t = str(s).strip()
    if not t:
        return None

    # remover NBSP e espaços
    t = t.replace("\u00A0", " ")
    t = t.replace(" ", "")

    # remover parênteses exteriores simples (ex.: "(1200)")
    if t.startswith("(") and t.endswith(")"):
        t = t[1:-1]

    # remover pontuação final (ex.: "2,500." -> "2,500")
    t = TRAILING_JUNK_RE.sub("", t)

    if not t:
        return None

    # Caso com ambos os separadores: decide decimal pelo último separador
    if "." in t and "," in t:
        last_dot = t.rfind(".")
        last_comma = t.rfind(",")

        if last_comma > last_dot:
            # Ex.: 1.234,56 (PT/ES)
            t = t.replace(".", "")
            t = t.replace(",", ".")
        else:
            # Ex.: 1,234.56 (EN)
            t = t.replace(",", "")

    else:
        # Só ponto
        if "." in t and "," not in t:
            # milhares PT/ES
            if THOUSANDS_DOT_RE.match(t):
                t = t.replace(".", "")
            # senão assume decimal e mantém

        # Só vírgula
        elif "," in t and "." not in t:
            # milhares EN
            if THOUSANDS_COMMA_RE.match(t):
                t = t.replace(",", "")
            else:
                # decimal PT/ES: 12,5 -> 12.5
                if t.count(",") > 1:
                    return None
                t = t.replace(",", ".")

        # Sem separadores: mantém

    # valida e converte
    if not SIMPLE_FLOAT_RE.match(t):
        return None

    try:
        return float(t)
    except ValueError:
        return None