"""Which environment variables hold the Anthropic API key, in preference order.

Default is the vendor-standard ANTHROPIC_API_KEY. Operators who keep several
Anthropic keys (e.g. one per billing account) set
SIMULACRUM_ANTHROPIC_API_KEY_ENV to a comma-separated list of env-var NAMES;
the first one that is set and non-empty wins. Values never go in that list.
"""

from __future__ import annotations

import os

DEFAULT_ANTHROPIC_API_KEY_ENV_VARS: tuple[str, ...] = ("ANTHROPIC_API_KEY",)
ANTHROPIC_API_KEY_ENV_OVERRIDE = "SIMULACRUM_ANTHROPIC_API_KEY_ENV"


def anthropic_api_key_env_vars() -> tuple[str, ...]:
    raw = os.environ.get(ANTHROPIC_API_KEY_ENV_OVERRIDE, "").strip()
    if not raw:
        return DEFAULT_ANTHROPIC_API_KEY_ENV_VARS
    names = tuple(n.strip() for n in raw.split(",") if n.strip())
    if not names:
        # An explicit override that names nothing must not silently fall back
        # to the default key (and possibly another billing account).
        raise RuntimeError(f"{ANTHROPIC_API_KEY_ENV_OVERRIDE} is set but names no environment variables")
    return names


def anthropic_api_key() -> str | None:
    for name in anthropic_api_key_env_vars():
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return None


def missing_key_message(purpose: str = "") -> str:
    names = " or ".join(anthropic_api_key_env_vars())
    suffix = f" {purpose}" if purpose else ""
    return (
        f"{names} required{suffix} (key-name order is configurable via "
        f"{ANTHROPIC_API_KEY_ENV_OVERRIDE})"
    )
