import unittest
import json
import string
import os
import importlib.util
from pathlib import Path
import sys
import types

# Créer des modules factices pour les dépendances natives absentes (bcrypt, psycopg2)
# Ces modules seront remplacés par des mocks dans les tests via patch.object
if 'bcrypt' not in sys.modules:
    bcrypt_mod = types.ModuleType('bcrypt')
    bcrypt_mod.hashpw = lambda pw, salt: b'hash'
    bcrypt_mod.gensalt = lambda: b'salt'
    sys.modules['bcrypt'] = bcrypt_mod

if 'psycopg2' not in sys.modules:
    psycopg2_mod = types.ModuleType('psycopg2')
    psycopg2_mod.connect = lambda *a, **k: None
    sys.modules['psycopg2'] = psycopg2_mod
from unittest.mock import patch, MagicMock

# Charger handler.py directement depuis le fichier pour éviter les imports relatifs
spec = importlib.util.spec_from_file_location(
    "handler", str(Path(__file__).parent / "handler.py")
)
handler = importlib.util.module_from_spec(spec)
spec.loader.exec_module(handler)


class TestGeneratePassword(unittest.TestCase):
    """Test suite for password generation and user creation handler"""

    @patch.object(handler, 'psycopg2')
    @patch.object(handler, 'bcrypt')
    def test_handle_with_valid_username(self, mock_bcrypt, mock_psycopg2):
        """Test successful user creation with valid username"""
        # Setup mocks
        mock_bcrypt.hashpw.return_value = b'hashed_password'
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_psycopg2.connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Execute
        payload = json.dumps({"username": "testuser"})
        result, status_code = handler.handle(payload)

        # Assertions
        assert status_code == 201
        assert result["message"] == "User created successfully."
        assert "password" in result
        assert len(result["password"]) == 24
        assert mock_psycopg2.connect.called

    @patch.object(handler, 'psycopg2')
    @patch.object(handler, 'bcrypt')
    def test_handle_without_username(self, mock_bcrypt, mock_psycopg2):
        """Test error handling when username is missing"""
        # Execute
        payload = json.dumps({"is_expired": False})
        result = handler.handle(payload)

        # Assertions
        assert result["statusCode"] == 400
        assert result["body"] == "Username required."
        assert not mock_psycopg2.connect.called

    @patch.object(handler, 'psycopg2')
    @patch.object(handler, 'bcrypt')
    def test_handle_with_empty_request(self, mock_bcrypt, mock_psycopg2):
        """Test error handling with empty request"""
        # Execute
        result = handler.handle(None)

        # Assertions
        assert result["statusCode"] == 400
        assert result["body"] == "Username required."

    @patch.object(handler, 'psycopg2')
    @patch.object(handler, 'bcrypt')
    def test_password_contains_required_characters(self, mock_bcrypt, mock_psycopg2):
        """Test that generated password contains uppercase, lowercase, digits and punctuation"""
        # Setup mocks
        mock_bcrypt.hashpw.return_value = b'hashed_password'
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_psycopg2.connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Execute
        payload = json.dumps({"username": "testuser"})
        result, status_code = handler.handle(payload)

        # Assertions
        password = result["password"]
        assert any(c.islower() for c in password), "Password should contain lowercase letters"
        assert any(c.isupper() for c in password), "Password should contain uppercase letters"
        assert any(c.isdigit() for c in password), "Password should contain digits"
        assert any(c in string.punctuation for c in password), "Password should contain punctuation"

    @patch.object(handler, 'psycopg2')
    @patch.object(handler, 'bcrypt')
    def test_handle_with_is_expired_true(self, mock_bcrypt, mock_psycopg2):
        """Test user creation with is_expired flag set to True"""
        # Setup mocks
        mock_bcrypt.hashpw.return_value = b'hashed_password'
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_psycopg2.connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Execute
        payload = json.dumps({"username": "testuser", "is_expired": True})
        result, status_code = handler.handle(payload)

        # Assertions
        assert status_code == 201
        assert result["message"] == "User created successfully."
        # Verify execute was called with password expiration date
        assert mock_cursor.execute.called

    @patch.object(handler, 'psycopg2')
    @patch.object(handler, 'bcrypt')
    def test_handle_with_is_expired_false(self, mock_bcrypt, mock_psycopg2):
        """Test user creation with is_expired flag set to False (180-day expiration)"""
        # Setup mocks
        mock_bcrypt.hashpw.return_value = b'hashed_password'
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_psycopg2.connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Execute
        payload = json.dumps({"username": "testuser", "is_expired": False})
        result, status_code = handler.handle(payload)

        # Assertions
        assert status_code == 201
        assert result["message"] == "User created successfully."

    @patch.object(handler, 'psycopg2')
    @patch.object(handler, 'bcrypt')
    def test_handle_database_error(self, mock_bcrypt, mock_psycopg2):
        """Test error handling when database connection fails"""
        # Setup mocks
        mock_bcrypt.hashpw.return_value = b'hashed_password'
        mock_psycopg2.connect.side_effect = Exception("Database connection failed")

        # Execute
        payload = json.dumps({"username": "testuser"})
        result, status_code = handler.handle(payload)

        # Assertions
        assert status_code == 500
        assert result["statut"] == "Error"
        assert "Database connection failed" in result["details"]

    @patch.object(handler, 'psycopg2')
    @patch.object(handler, 'bcrypt')
    def test_password_length(self, mock_bcrypt, mock_psycopg2):
        """Test that generated password has exactly 24 characters"""
        # Setup mocks
        mock_bcrypt.hashpw.return_value = b'hashed_password'
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_psycopg2.connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Execute
        payload = json.dumps({"username": "testuser"})
        result, status_code = handler.handle(payload)

        # Assertions
        assert len(result["password"]) == 24

    @patch.object(handler, 'psycopg2')
    @patch.object(handler, 'bcrypt')
    def test_database_called_with_correct_parameters(self, mock_bcrypt, mock_psycopg2):
        """Test that database is called with correct environment variables"""
        # Setup mocks
        mock_bcrypt.hashpw.return_value = b'hashed_password'
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_psycopg2.connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Execute
        with patch.dict(os.environ, {
            'DB_HOST': 'localhost',
            'DB_USER': 'postgres',
            'DB_PWD': 'password',
            'DB_NAME': 'faas_db'
        }):
            payload = json.dumps({"username": "testuser"})
            result, status_code = handler.handle(payload)

        # Assertions
        mock_psycopg2.connect.assert_called_once_with(
            host='localhost',
            user='postgres',
            password='password',
            dbname='faas_db'
        )


if __name__ == '__main__':
    unittest.main()
