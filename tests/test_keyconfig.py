"""Anthropic key-name resolution: standard name by default, order configurable."""
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'fly_v8'))

from agents.keyconfig import anthropic_api_key, missing_key_message  # noqa: E402


class KeyConfigTest(unittest.TestCase):
    def test_default_is_standard_name(self):
        env = {'ANTHROPIC_API_KEY': 'generic-key', 'ORG_ANTHROPIC_API_KEY': 'org-key'}
        with patch.dict(os.environ, env, clear=True):
            self.assertEqual(anthropic_api_key(), 'generic-key')

    def test_unconfigured_names_are_ignored(self):
        with patch.dict(os.environ, {'ORG_ANTHROPIC_API_KEY': 'org-key'}, clear=True):
            self.assertIsNone(anthropic_api_key())
            self.assertIn('ANTHROPIC_API_KEY', missing_key_message())

    def test_configured_order_wins(self):
        env = {
            'SIMULACRUM_ANTHROPIC_API_KEY_ENV': 'ORG_ANTHROPIC_API_KEY, ANTHROPIC_API_KEY',
            'ORG_ANTHROPIC_API_KEY': 'org-key',
            'ANTHROPIC_API_KEY': 'generic-key',
        }
        with patch.dict(os.environ, env, clear=True):
            self.assertEqual(anthropic_api_key(), 'org-key')

    def test_configured_order_falls_through_unset_names(self):
        env = {
            'SIMULACRUM_ANTHROPIC_API_KEY_ENV': 'ORG_ANTHROPIC_API_KEY,ANTHROPIC_API_KEY',
            'ORG_ANTHROPIC_API_KEY': '  ',
            'ANTHROPIC_API_KEY': 'generic-key',
        }
        with patch.dict(os.environ, env, clear=True):
            self.assertEqual(anthropic_api_key(), 'generic-key')


if __name__ == '__main__':
    unittest.main()
