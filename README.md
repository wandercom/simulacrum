# Simulacrum

Adversarial dialog tool: pitch an idea, test a definition, or challenge an
architectural assumption. Includes a Python CLI, HTTP API, and browser chat UI.
It models Jeremy McEntire's reasoning style; its output is not Jeremy's advice
or a source of private biographical facts.

## Run locally

Python 3.12 or 3.13 (the pinned dependencies were checked with 3.13):

```sh
python3.13 -m venv .venv
. .venv/bin/activate
pip install -r fly_v8/requirements.txt
# Supply WANDER_ANTHROPIC_API_KEY or ANTHROPIC_API_KEY in your environment.
python run.py 'Every team needs a strong manager.'
python run.py --spice spicy 'Every team needs a strong manager.'
uvicorn app:app --app-dir fly_v8 --host 127.0.0.1 --port 8080
```

Open http://127.0.0.1:8080 for chat. For API clients:

```sh
curl http://127.0.0.1:8080/chat \
  -H 'Content-Type: application/json' \
  -d '{"dialog":[{"role":"Interlocutor","text":"Every team needs a strong manager."}]}'
```

The client supplies the full dialog for follow-ups. The CLI accepts `--history`
pointing to a JSON array of `[role, text]` pairs; keep conversation files outside
this repository. Run `python run.py --help` for options.

## Configuration

- `WANDER_ANTHROPIC_API_KEY`, `ANTHROPIC_API_KEY`, `JMC_ANTHROPIC_API_KEY`:
  first nonempty key wins, in that order.
- `SIMULACRUM_MODEL`: Anthropic model override (default `claude-sonnet-4-6`).
- `GENERALIST_MODEL` and `OPENAI_API_KEY`: optional recall branch. Both are
  required to enable your own model. No private model identifier, model weights,
  or biography is bundled. With no `GENERALIST_MODEL`, all turns use Anthropic.
- `SIMULACRUM_TOKEN`: stable cookie-signing secret for the web app. Despite its
  legacy name, this is **not** an API bearer token or access-control mechanism.
- `TURNSTILE_SECRET` and `TURNSTILE_SITE_KEY`: optional browser bot check.

Chat sends dialog and the bundled examples to the configured model provider.
The web app has no login. Its signed-cookie request cap is per browser; clearing
cookies resets it. Bind locally for development. A shared deployment needs its
operator's access controls and provider budget limits. Cookie persistence uses
HTTPS. No deployment is created by this repository.

## Container

```sh
docker build -t simulacrum ./fly_v8
docker run --rm -p 127.0.0.1:8080:8080 \
  -e ANTHROPIC_API_KEY simulacrum
```

## Checks

```sh
python -m unittest discover -s tests -v
```

These checks cover startup without OpenAI, chat and mode selection, optional
recall configuration, and the bundled corpus identity. They use an HTTP mock at
the model-provider boundary. Live model responses need a configured key.

## Contents and provenance

Serving code is copied from the source working tree, including its existing
uncommitted routing changes. See [EXPORT.md](EXPORT.md) for the privacy boundary.
[PRIMER.md](PRIMER.md) is the general research/building guide; its pipeline
examples describe the original research process, not bundled runtime commands.
