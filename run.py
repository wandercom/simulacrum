#!/usr/bin/env python3
"""Run the bundled Simulacrum dispatcher from a shell or agent tool."""
import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('question', nargs='?', help='Prompt; reads stdin if omitted')
    parser.add_argument('--history', type=Path, help='JSON array of [role, text] pairs')
    parser.add_argument('--spice', choices=['tuned', 'spicy'], default='tuned')
    args = parser.parse_args()
    question = args.question if args.question is not None else sys.stdin.read()
    if not question.strip():
        parser.error('question must not be empty')
    history = json.loads(args.history.read_text()) if args.history else []
    if not isinstance(history, list) or any(
        not isinstance(turn, list) or len(turn) != 2
        or not all(isinstance(value, str) for value in turn) for turn in history
    ):
        parser.error('history must be a JSON array of [role, text] pairs')
    sys.path.insert(0, str(Path(__file__).resolve().parent / 'fly_v8'))
    from agents.dispatcher import Dispatcher
    dialogue = [(role, text) for role, text in history]
    dialogue.append(('Interlocutor', question))
    print(Dispatcher().utterance(dialogue, spice=args.spice)['text'])


if __name__ == '__main__':
    main()
