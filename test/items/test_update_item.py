import unittest
import psycopg2
from unittest.mock import MagicMock, patch
import json
from api.items.update_item.update_item import lambda_handler, decimal_default

class TestUpdateItem(unittest.TestCase):
    def setUp(self):
        self.mock_description = [
            ("id",), ("name",), ("price",), ("description",), ("created_at",)
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

    @patch("api.items.update_item.update_item.get_db_connection")
    def test_lambda_handler_updates_expected_item(self, mock_get_db_connection):
        self.setup_mock_db(mock_get_db_connection, fetchone=(1, "Updated Item", 1.99, "Test Item Description"))

        event = {'pathParameters' : {'id' : '1'}, 'body' : json.dumps({'name' : 'Updated Item', 'price': 1.99, 'description': 'Test Item Description'})}
        expectedResponseBody = {'id': 1, 'name' : 'Updated Item', 'price': 1.99, 'description': 'Test Item Description'}

        response = lambda_handler(event,None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)

    def test_lambda_handler_update_item_throws_error_with_incorrect_path(self):
        event = {'pathParameters' : {'id' : ''}, 'body' : json.dumps({'name' : 'Updated', 'price': 1.99, 'description': 'Test Item Description'})}

        response = lambda_handler(event,None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Invalid or missing ID in path or request data")

    def test_lambda_handler_update_item_throws_error_with_missing_path(self):
        event = {'body' : json.dumps({'name' : 'Updated', 'price': 1.99, 'description': 'Test Item Description'})}

        response = lambda_handler(event,None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Invalid or missing ID in path or request data")

    def test_lambda_handler_update_item_throws_error_with_incorrect_body(self):
        event = {'pathParameters' : {'id' : '1'}, 'body' : json.dumps({'nme' : 'Updated'})}

        response = lambda_handler(event,None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Invalid or missing ID in path or request data")

    def test_lambda_handler_update_item_throws_error_with_missing_body(self):
        event = {'pathParameters' : {'id' : '1'}}

        response = lambda_handler(event,None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Invalid or missing ID in path or request data")

    @patch("api.items.update_item.update_item.get_db_connection")
    def test_lambda_handler_update_item_throws_error_if_row_not_returned(self, mock_get_db_connection):
        self.setup_mock_db(mock_get_db_connection, fetchone=())

        event = {'pathParameters' : {'id' : '1'}, 'body' : json.dumps({'name' : 'Updated', 'price': 1.99, 'description': 'Test Item Description'})}
        
        response = lambda_handler(event,None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(body["error"], "No Active Item found at ID: 1")

    @patch("api.items.update_item.update_item.get_db_connection")
    def test_lambda_handler_update_item_throws_error_when_db_has_error(self, mock_get_db_connection):
        self.setup_mock_db(mock_get_db_connection, side_effect=psycopg2.Error)

        event = {'pathParameters' : {'id' : '1'}, 'body' : json.dumps({'name' : 'Updated', 'price': 1.99, 'description': 'Test Item Description'})}

        response = lambda_handler(event,None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(body["error"], "Database error")

    def test_default_decimal_handles_datetime(self):
        self.assertEqual("1", decimal_default(1))

    def test_default_decimal_handles_string(self):
        self.assertEqual("String Object", decimal_default("String Object"))

    def test_default_json_handles_float(self):
        self.assertEqual("1.99", decimal_default(1.99))