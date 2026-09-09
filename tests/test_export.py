"""Exercise the distributable with only fake provider credentials and transport."""
import hashlib
import importlib
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import httpx
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'fly_v8'))


class ExportTest(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}, clear=True)
        self.env.start()
        self.requests = []

        original_send = httpx.Client.send

        def provider(client, request, *args, **kwargs):
            if request.url.host == "testserver":
                return original_send(client, request, *args, **kwargs)
            assert request.url.host == "api.anthropic.com"
            body = json.loads(request.content)
            self.requests.append(body)
            prompt = body['messages'][0]['content']
            text = ('MODE: A\nREASON: Explicit criterion and debate invitation'
                    if prompt.startswith('Determine whether') else 'Which constraint requires a manager?')
            return httpx.Response(200, request=request, json={
                'id': 'msg_test', 'type': 'message', 'role': 'assistant',
                'model': body['model'], 'content': [{'type': 'text', 'text': text}],
                'stop_reason': 'end_turn', 'stop_sequence': None,
                'usage': {'input_tokens': 10, 'output_tokens': 10},
            })

        self.transport = patch.object(httpx.Client, 'send', provider)
        self.transport.start()
        sys.modules.pop('app', None)
        self.app = importlib.import_module('app')
        self.client = TestClient(self.app.app, base_url='https://testserver')

    def tearDown(self):
        self.client.close()
        self.transport.stop()
        self.env.stop()

    def test_starts_without_openai_and_serves_ui(self):
        self.assertEqual(self.client.get('/healthz').json()['agents'], ['v9.1'])
        for path in ['/', '/privacy', '/terms', '/config']:
            self.assertEqual(self.client.get(path).status_code, 200)

    def test_chat_modes_and_follow_up(self):
        for spice in ['tuned', 'spicy']:
            self.assertEqual(self.client.post('/spice', data={'spice': spice}).status_code, 200)
            response = self.client.post('/chat', json={'dialog': [
                {'role': 'Interlocutor', 'text': 'I define success as profit. Prove me wrong.'},
                {'role': 'Jeremy', 'text': 'Over what period?'},
                {'role': 'Interlocutor', 'text': 'Over one year. Give a counterexample.'},
            ]})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['phase'], 'SPECIALIST')
            self.assertEqual(response.json()['mode'], 'A')
            self.assertTrue(response.json()['response'])
            self.assertIn('Over one year', self.requests[-1]['messages'][0]['content'])
            self.assertIn('MODE OVERRIDE', self.requests[-1]['system'][-1]['text'])
        self.assertEqual(self.client.post('/chat', json={'dialog': []}).status_code, 400)

    def test_optional_recall_needs_explicit_credentials(self):
        from agents.dispatcher import Dispatcher
        with patch.dict(os.environ, {'GENERALIST_MODEL': 'test-optional-model'}):
            with self.assertRaisesRegex(RuntimeError, 'OPENAI_API_KEY required'):
                Dispatcher()
            with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-openai-key'}):
                self.assertEqual(Dispatcher()._generalist.model, 'test-optional-model')

    def test_corpus_is_exact_public_blob(self):
        data = (ROOT / 'fly_v8/data/adversarial_pairs_annotated.json').read_bytes()
        self.assertEqual(len(json.loads(data)), 11)
        digest = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        self.assertEqual(digest, 'f69a16b9fad060b2e1c578c6ad60c56c35289a99')


if __name__ == '__main__':
    unittest.main()
