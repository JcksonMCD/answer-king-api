import unittest
import psycopg2
from unittest.mock import MagicMock, patch
import json
from api.categories.get_all_categories.get_all_categories import lambda_handler, json_default
import datetime

class TestGetAllCategories(unittest.TestCase):
    def setUp(self):
        self.mock_rows = [
            (1, "Test Category", datetime.datetime(2025, 7, 2, 12, 0, 0))
        ]
        self.mock_description = [
            ("id",), ("name",), ("created_at",)
        ]

    @patch("api.categories.get_all_categories.get_all_categories.get_db_connection")
    def test_lambda_handler_returns_expected_categories(self, mock_get_db_connection):
        # Mock Cursor
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = self.mock_rows
        mock_cursor.description = self.mock_description

        #Mock Connection
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn

        expectedResponseBody = [{'id': 1, 'name': 'Test Category', 'created_at': '2025-07-02T12:00:00'}]

        response = lambda_handler({},None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)

    @patch("api.categories.get_all_categories.get_all_categories.get_db_connection")
    def test_lambda_handler_throws_database_error(self, mock_get_db_connection):
        mock_get_db_connection.side_effect = psycopg2.Error('DB Error')

        response = lambda_handler({},None)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Database error', response['body'])

    def test_default_json_handles_datetime(self):
        dateObj = datetime.datetime(2025, 7, 2)
        self.assertEqual(dateObj.isoformat(), json_default(dateObj))

    def test_default_json_handles_string(self):
        stringObj = "String Object"
        self.assertEqual("String Object", json_default(stringObj))

    def test_default_json_handles_float(self):
        floatObj = 1.99
        self.assertEqual("1.99", json_default(floatObj))
