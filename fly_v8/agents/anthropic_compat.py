"""Claude 5-family compatibility helpers, shared by dispatcher and specialist.

Claude 5-family models (claude-{fable,opus,sonnet,haiku}-5[-*]) reject the
deprecated `temperature` parameter and think by default, which breaks callers
that expect a text-only contract. Two adjustments are needed:

  1. Omit `temperature` and pass `thinking={"type": "disabled"}` instead, for
     any Claude 5-family model.
  2. Responses from these models may lead with a thinking content block, so
     callers must scan for the first text-type block rather than assume
     `resp.content[0]`.

Mirrors the reference implementation in ~/.claude/skills/simulacrum/run.py.
"""

from __future__ import annotations

import re

_CLAUDE_5_FAMILY = re.compile(r"^claude-(fable|opus|sonnet|haiku)-5($|-)")


def anthropic_kwargs(model: str, temperature: float) -> dict:
    """Model-appropriate extra kwargs for an Anthropic messages.create call."""
    if _CLAUDE_5_FAMILY.match(model):
        return {"thinking": {"type": "disabled"}}
    return {"temperature": temperature}


def first_text(resp) -> str:
    """First text-type content block's text, stripped. Empty string if none."""
    for block in resp.content:
        if getattr(block, "type", "") == "text":
            return block.text.strip()
    return ""
