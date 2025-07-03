import unittest
import psycopg2
from unittest.mock import MagicMock, patch
import json
from api.categories.create_category.create_category import lambda_handler
import datetime

class TestCreateCategory(unittest.TestCase):
    def setUp(self):
        self.mock_description = [
            ("id",), ("name",), ("created_at",)
        ]

    def setup_mock_db(self, mock_get_db_connection, fetchone=None, side_effect=None):
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = fetchone
        if side_effect:
            mock_cursor.fetchone.side_effect = side_effect
        mock_cursor.description = self.mock_description

        mock_conn = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_db_connection.return_value.__enter__.return_value = mock_conn

    @patch("api.categories.create_category.create_category.get_db_connection")
    def test_lambda_handler_creates_expected_category(self, mock_get_db_connection):
        self.setup_mock_db(mock_get_db_connection, fetchone=(1, datetime.datetime(2025, 7, 2, 12, 0, 0)))

        event = {'body' : json.dumps({'name' : 'Created'})}
        expectedResponseBody = {'id': 1, 'name': 'Created', 'created_at': '2025-07-02T12:00:00'}

        response = lambda_handler(event,None)

        self.assertEqual(response['statusCode'], 201)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)

    def test_lambda_handler_create_category_throws_error_with_incorrect_body(self):
        event = {'body' : json.dumps({'' : 'Created'})}

        response = lambda_handler(event,None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Invalid request data")

    def test_lambda_handler_create_category_throws_error_with_body_as_string(self):
        event = {'body' : 'name : Created'}

        response = lambda_handler(event,None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Invalid request data")

    def test_lambda_handler_create_category_throws_error_with_missing_body(self):
        response = lambda_handler({},None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Invalid request data")

    @patch("api.categories.create_category.create_category.get_db_connection")
    def test_lambda_handler_create_category_throws_error_when_db_has_error(self, mock_get_db_connection):
        self.setup_mock_db(mock_get_db_connection, side_effect=psycopg2.Error)

        event = {'body' : json.dumps({'name' : 'Created'})}

        response = lambda_handler(event,None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(body["error"], "Database error")
