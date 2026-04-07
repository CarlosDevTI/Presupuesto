from __future__ import annotations

import re
import unicodedata

AREA_EQUIVALENTS = {
    "GER ADMON": "GER. ADMON",
    "GER COMERCIAL": "GER. COMERCIAL",
    "GER TI": "GER. TI",
}


def normalize_area_name(value: object, fallback: str | None = None) -> str | None:
    raw_value = str(value or fallback or "").strip()
    if not raw_value:
        return None

    cleaned = re.sub(r"\s+", " ", raw_value).upper()
    comparison_key = _ascii_key(cleaned).replace(".", "")
    return AREA_EQUIVALENTS.get(comparison_key, cleaned)


def _ascii_key(value: str) -> str:
    return unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
