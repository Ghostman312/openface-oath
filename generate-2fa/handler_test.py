import unittest
import json
import os
import importlib.util
from pathlib import Path
import sys
import types
from unittest.mock import patch, MagicMock

# Faux modules pour l'import de handler
if 'pyotp' not in sys.modules:
    pyotp_mod = types.ModuleType('pyotp')
    class TOTP:
        def __init__(self, key):
            self.key = key
        def provisioning_uri(self, name, issuer_name=None):
            return f"otpauth://totp/{issuer_name}:{name}?secret={self.key}"
    pyotp_mod.totp = types.SimpleNamespace(TOTP=TOTP)
    sys.modules['pyotp'] = pyotp_mod

if 'psycopg2' not in sys.modules:
    psycopg2_mod = types.ModuleType('psycopg2')
    psycopg2_mod.connect = lambda *a, **k: None
    sys.modules['psycopg2'] = psycopg2_mod

# Charger handler.py depuis le fichier
spec = importlib.util.spec_from_file_location(
    "handler", str(Path(__file__).parent / "handler.py")
)
handler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(handler)


class TestGenerate2FA(unittest.TestCase):

    @patch.object(handler, 'psycopg2')
    def test_missing_username(self, mock_psycopg2):
        res = handler.handle(None)
        # handler returns a dict for error without tuple in some handlers
        if isinstance(res, tuple):
            result, status = res
            assert status == 400
        else:
            assert res.get("statusCode") == 400

    @patch.object(handler, 'psycopg2')
    def test_successful_totp_creation(self, mock_psycopg2):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_psycopg2.connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        payload = json.dumps({"username": "user1"})
        result, status_code = handler.handle(payload)

        assert status_code == 201
        assert result["message"] == "TOTP created successfully."
        assert "totp" in result
        assert mock_cursor.execute.called

    @patch.object(handler, 'psycopg2')
    def test_db_error(self, mock_psycopg2):
        mock_psycopg2.connect.side_effect = Exception("DB fail")
        payload = json.dumps({"username": "user1"})
        result, status_code = handler.handle(payload)
        assert status_code == 500
        assert result["statut"] == "Error"


if __name__ == '__main__':
    unittest.main()

