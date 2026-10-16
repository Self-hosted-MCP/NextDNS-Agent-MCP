# SPDX-License-Identifier: Apache-2.0
"""Languages for the web pages (coming with the settings page). Tool answers stay in English: the AI app reads them
and talks to the user in the user's own language.

Texts a person sees on a page are written in English inside _("..."). A language is a JSON file,
locales/<code>.json, mapping each English text to its translation. Missing texts fall back to English.
Only English exists so far.
"""

from __future__ import annotations

import contextvars
import json
from pathlib import Path

PACKAGE_LOCALES = Path(__file__).resolve().parent / "locales"
LANGUAGES = {"en": "English"}

LANG: contextvars.ContextVar[str] = contextvars.ContextVar("lang", default="en")
_catalogs: dict[str, dict[str, str]] = {}


def catalog(code: str) -> dict[str, str]:
    if code == "en":
        return {}
    if code not in _catalogs:
        path = PACKAGE_LOCALES / f"{code}.json"
        try:
            found = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
        except (OSError, ValueError):
            found = {}
        _catalogs[code] = {k: v for k, v in found.items() if isinstance(v, str) and v.strip()}
    return _catalogs[code]


def _(text: str, **values) -> str:
    """The text in the current page's language, with {placeholders} filled in."""
    out = catalog(LANG.get()).get(text, text)
    return out.format(**values) if values else out


def N_(text: str) -> str:
    """Marks a text for translation where it's stored first and translated later."""
    return text
