"""Derive the canonical dusun name from a household address."""
from __future__ import annotations

import re


CANONICAL_DUSUNS = ('BOJONGIRENG', 'PANUMBANGAN', 'SIMENDEM', 'SASAK', 'MANDELUN')


def canonical_dusun(alamat: str | None) -> str | None:
    """Return one supported dusun found as a whole word, otherwise None.

    Prefixes such as ``DK``, ``DK.``, or ``DUSUN`` are deliberately ignored;
    only the canonical name is persisted. An address naming more than one
    supported dusun is treated as ambiguous instead of guessing.
    """
    if not alamat:
        return None
    found = [name for name in CANONICAL_DUSUNS if re.search(rf'(?<!\w){name}(?!\w)', alamat, re.IGNORECASE)]
    return found[0] if len(found) == 1 else None
