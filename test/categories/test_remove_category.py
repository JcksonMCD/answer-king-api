import unittest
import psycopg2
from unittest.mock import MagicMock, patch
import json
from api.categories.remove_category.remove_category import lambda_handler

class TestRemoveCategory(unittest.TestCase):
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

    @patch("api.categories.remove_category.remove_category.get_db_connection")
    def test_lambda_handler_removes_expected_category(self, mock_get_db_connection):
        self.setup_mock_db(mock_get_db_connection, fetchone=(1,))

        event = {'pathParameters' : {'id' : '1'}}
        expectedResponseBody = {'deleted_category_id': 1}

        response = lambda_handler(event,None)

        self.assertEqual(response['statusCode'], 204)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)

    @patch("api.categories.remove_category.remove_category.get_db_connection")
    def test_lambda_handler_throws_error_when_db_errors(self, mock_get_db_connection):
        self.setup_mock_db(mock_get_db_connection, side_effect=psycopg2.Error)

        event = {'pathParameters' : {'id' : '1'}}
        expectedResponseBody = {'error': 'Database error'}

        response = lambda_handler(event,None)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)

    @patch("api.categories.remove_category.remove_category.get_db_connection")
    def test_lambda_handler_throws_error_when_db_returns_nothing(self, mock_get_db_connection):
        self.setup_mock_db(mock_get_db_connection, fetchone=())

        event = {'pathParameters' : {'id' : '1'}}
        expectedResponseBody = {'error': 'No Category found at ID: 1'}

        response = lambda_handler(event,None)

        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)

    def test_lambda_handler_remove_category_throws_error_with_incorrect_path(self):
        event = {'pathParameters' : {'id' : ''}}

        response = lambda_handler(event,None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Invalid or missing ID in path")

    def test_lambda_handler_remove_category_throws_error_with_non_numerical_path(self):
        event = {'pathParameters' : {'id' : 'c'}}

        response = lambda_handler(event,None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Invalid or missing ID in path")

    def test_lambda_handler_remove_category_throws_error_with_missing_path(self):
        response = lambda_handler({},None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Invalid or missing ID in path")



