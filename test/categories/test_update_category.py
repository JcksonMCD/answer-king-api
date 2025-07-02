import unittest
import psycopg2
from unittest.mock import MagicMock, patch
import json
from api.categories.update_category.update_category import lambda_handler, json_default
import datetime

class TestGetAllCategories(unittest.TestCase):
    def setUp(self):
        self.mock_description = [
            ("id",), ("name",), ("created_at",)
        ]

    @patch("api.categories.update_category.update_category.get_db_connection")
    def test_lambda_handler_updates_expected_category(self, mock_get_db_connection):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1, "Updated")
        mock_cursor.description = self.mock_description


        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn

        event = {'pathParameters' : {'id' : '1'}, 'body' : json.dumps({'name' : 'Updated'})}
        expectedResponseBody = {'id': 1, 'name': 'Updated'}

        response = lambda_handler(event,None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)

    def test_default_json_handles_datetime(self):
        dateObj = datetime.datetime(2025, 7, 2)
        self.assertEqual(dateObj.isoformat(), json_default(dateObj))

    def test_default_json_handles_string(self):
        stringObj = "String Object"
        self.assertEqual("String Object", json_default(stringObj))

    def test_default_json_handles_float(self):
        floatObj = 1.99
        self.assertEqual("1.99", json_default(floatObj))
