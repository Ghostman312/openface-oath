import unittest
import json
import importlib.util
from pathlib import Path
import sys
import types
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Faux modules pour l'import
if 'pyotp' not in sys.modules:
    pyotp_mod = types.ModuleType('pyotp')
    class TOTP:
        def __init__(self, key):
            self.key = key
        def verify(self, code):
            return True
    pyotp_mod.TOTP = TOTP
    sys.modules['pyotp'] = pyotp_mod

if 'bcrypt' not in sys.modules:
    bcrypt_mod = types.ModuleType('bcrypt')
    bcrypt_mod.checkpw = lambda pw, h: True
    sys.modules['bcrypt'] = bcrypt_mod

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


class TestAuthenticate(unittest.TestCase):

    @patch.object(handler, 'psycopg2')
    def test_invalid_username(self, mock_psycopg2):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn.cursor.return_value = mock_cursor
        mock_psycopg2.connect.return_value = mock_conn

        payload = json.dumps({"username": "nope"})
        result, status = handler.handle(payload)

        assert status == 400
        assert result["authenticated"] is False

    @patch.object(handler, 'psycopg2')
    def test_password_expired(self, mock_psycopg2):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        past = datetime.now() - timedelta(days=1)
        mock_cursor.fetchone.return_value = ("hash", None, past)
        mock_conn.cursor.return_value = mock_cursor
        mock_psycopg2.connect.return_value = mock_conn

        payload = json.dumps({"username": "user", "password": "p"})
        result, status = handler.handle(payload)

        assert status == 401
        assert result["expired"] is True

    @patch.object(handler, 'psycopg2')
    @patch.object(handler, 'bcrypt')
    def test_wrong_password(self, mock_bcrypt, mock_psycopg2):
        mock_bcrypt.checkpw.return_value = False
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("hash", None, None)
        mock_conn.cursor.return_value = mock_cursor
        mock_psycopg2.connect.return_value = mock_conn

        payload = json.dumps({"username": "user", "password": "bad"})
        result, status = handler.handle(payload)
        assert status == 400
        assert result["authenticated"] is False

    @patch.object(handler, 'psycopg2')
    @patch.object(handler, 'bcrypt')
    def test_missing_totp_code(self, mock_bcrypt, mock_psycopg2):
        mock_bcrypt.checkpw.return_value = True
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("hash", "somekey", None)
        mock_conn.cursor.return_value = mock_cursor
        mock_psycopg2.connect.return_value = mock_conn

        payload = json.dumps({"username": "user", "password": "p"})
        result, status = handler.handle(payload)
        assert status == 400
        assert result["message"] == "TOTP code required."

    @patch.object(handler, 'psycopg2')
    @patch.object(handler, 'bcrypt')
    @patch.object(handler, 'pyotp')
    def test_invalid_totp_code(self, mock_pyotp, mock_bcrypt, mock_psycopg2):
        mock_bcrypt.checkpw.return_value = True
        # pyotp.TOTP.verify returns False
        mock_pyotp.TOTP.return_value.verify.return_value = False
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("hash", "key", None)
        mock_conn.cursor.return_value = mock_cursor
        mock_psycopg2.connect.return_value = mock_conn

        payload = json.dumps({"username": "user", "password": "p", "totp_code": "000000"})
        result, status = handler.handle(payload)
        assert status == 400
        assert result["message"] == "Invalid TOTP code."

    @patch.object(handler, 'psycopg2')
    @patch.object(handler, 'bcrypt')
    @patch.object(handler, 'pyotp')
    def test_successful_auth(self, mock_pyotp, mock_bcrypt, mock_psycopg2):
        mock_bcrypt.checkpw.return_value = True
        mock_pyotp.TOTP.return_value.verify.return_value = True
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("hash", "key", None)
        mock_conn.cursor.return_value = mock_cursor
        mock_psycopg2.connect.return_value = mock_conn

        payload = json.dumps({"username": "user", "password": "p", "totp_code": "123456"})
        result, status = handler.handle(payload)
        assert status == 200
        assert result["authenticated"] is True

    @patch.object(handler, 'psycopg2')
    def test_db_error(self, mock_psycopg2):
        mock_psycopg2.connect.side_effect = Exception("DB fail")
        payload = json.dumps({"username": "user", "password": "p"})
        result, status = handler.handle(payload)
        assert status == 500
        assert result["statut"] == "Error"


if __name__ == '__main__':
    unittest.main()

