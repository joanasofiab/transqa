from dataclasses import asdict
from typing import List, Dict, Any

import pandas as pd

from core.models import Alert
from checks.nontranslate import check_nontranslate
from checks.numbers import check_numbers
from checks.dates import check_dates
from checks.percentages import check_percentages
from checks.currencies import check_currencies
from checks.units import check_units
from checks.ranges import check_ranges
from checks.punctuation import check_punctuation
from checks.placeholders import check_placeholders

def run_all_checks(source: str, target: str, pair: str, config: Dict[str, Any]) -> List[Alert]:
    enabled = set(config.get("checks", {}).get("enabled", []))
    alerts: List[Alert] = []

    if "nontranslate" in enabled:
        alerts += check_nontranslate(source, target)

    if "numbers" in enabled:
        units = config.get("rules", {}).get("units", [])
        symbols = config.get("rules", {}).get("currency_symbols", ["€", "$", "£"])
        alerts += check_numbers(source, target, units=units, currency_symbols=symbols)
    
    if "dates" in enabled:
        warn_amb = bool(config.get("rules", {}).get("warn_ambiguous_numeric_dates", True))
        alerts += check_dates(source, target, warn_ambiguous=warn_amb)
    
    if "percentages" in enabled:
        alerts += check_percentages(source, target)

    if "currencies" in enabled:
        symbols = config.get("rules", {}).get("currency_symbols", ["€", "$", "£"])
        alerts += check_currencies(source, target, currency_symbols=symbols)

    if "units" in enabled:
        units = config.get("rules", {}).get("units", [])
        alerts += check_units(source, target, units=units)
    
    if "ranges" in enabled:
        alerts += check_ranges(source, target)

    if "punctuation" in enabled:
        alerts += check_punctuation(source, target)
    
    if "placeholders" in enabled:
        allow_reorder = bool(config.get("rules", {}).get("placeholders_allow_reorder", True))
        alerts += check_placeholders(source, target, allow_reorder=allow_reorder)

    sev_order = {"Critical": 0, "Warning": 1, "Info": 2}
    alerts.sort(key=lambda a: (sev_order.get(a.severity, 9), a.check))
    return alerts

def alerts_to_dataframe(alerts: List[Alert]) -> pd.DataFrame:
    cols = ["severity", "check", "source_evidence", "target_evidence", "message", "suggestion"]
    if not alerts:
        return pd.DataFrame(columns=cols)
    return pd.DataFrame([asdict(a) for a in alerts], columns=cols)