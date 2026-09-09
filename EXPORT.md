# Export boundary

This repository starts with a new git history. It does not copy git objects,
reflogs, hooks, remotes, or configuration from the original repository.

Included:

- `fly_v8` serving code and static UI, with the changes below.
- The 11-example corpus already published in `jmcentire/simulacrum-tools` at
  `fly/data/adversarial_pairs_annotated.json`. Verified against GitHub's public
  blob SHA `f69a16b9fad060b2e1c578c6ad60c56c35289a99` before export.
- The general `PRIMER.md` guide and the public tool's MIT license.

Excluded:

- The source's 51-example private corpus; only the published 11-example version
  is bundled. No other examples or source conversation records are imported.
- `agent_bank/`, `pipeline/`, `genagents/`, embeddings, interviews, transcripts,
  research/evaluation outputs, caches, credentials, and environment files.
- The private `.kin/` graph and `REEVE_GOVERNANCE_INTEGRATION.md`.
- The hardcoded personal fine-tune ID, embedded biography/project glossary,
  personal contact email, and existing Fly application target.

Runtime adjustments:

- Optional recall is off unless `GENERALIST_MODEL` is configured. The default
  specialist needs only an Anthropic key and uses the published examples.
- `SIMULACRUM_MODEL` configures specialist/classifier selection.
- Health reports the enabled agents; docs and links match this distribution.
- `run.py` exposes the same dispatcher to CLI callers.

Removing private examples and recall data changes behavioral coverage. This
export does not claim to reproduce the full private model's fidelity or recall.
Do not rsync the original tree wholesale into this repository for updates.
Review a file allowlist and compare corpus provenance before publishing changes.

## Verification at export

- Fresh Python 3.13 virtual environment installed the pinned requirements;
  `pip check` reported no broken requirements.
- Four automated checks passed, including API chat/follow-ups in both tone
  settings and an exact Git blob check for the published example corpus.
- Six live CLI calls (three nonsensitive prompts in each tone setting) returned
  responses from `claude-sonnet-4-6`, with OpenAI and private-data overrides
  removed from the process environment.
- Every excluded private example was checked for verbatim input/output residue
  in the exported text files; no such residue was found. Credentials, personal
  model ID, home-directory paths, and personal contact email scans passed.
- Docker execution and deployment were not performed.
