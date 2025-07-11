import unittest
import psycopg2
from unittest.mock import patch
import json
from api.items.update_item.update_item import lambda_handler
from test.helper_funcs.setup_mock_db import setup_mock_db

class TestUpdateItem(unittest.TestCase):
    def setUp(self):
        self.mock_description = [
            ("id",), ("name",), ("price",), ("description",), ("created_at",)
        ]

    @patch("api.items.update_item.update_item.get_db_connection")
    def test_lambda_handler_updates_expected_item(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchone=(1, "Updated Item", 1.99, "Test Item Description"), description=self.mock_description)

        event = {'pathParameters' : {'id' : '1'}, 'body' : json.dumps({'name' : 'Updated Item', 'price': 1.99, 'description': 'Test Item Description'})}
        expectedResponseBody = {'id': 1, 'name' : 'Updated Item', 'price': 1.99, 'description': 'Test Item Description'}

        response = lambda_handler(event,None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)

    @patch("api.items.update_item.update_item.get_db_connection")
    def test_lambda_handler_updates_expected_item_with_missing_description(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchone=(1, "Updated Item", 1.99), description=self.mock_description)

        event = {'pathParameters' : {'id' : '1'}, 'body' : json.dumps({'name' : 'Updated Item', 'price': 1.99})}
        expectedResponseBody = {'id': 1, 'name' : 'Updated Item', 'price': 1.99}

        response = lambda_handler(event,None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)

    @patch("api.items.update_item.update_item.get_db_connection")
    def test_lambda_handler_update_item_throws_error_if_row_not_returned(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchone=())

        event = {'pathParameters' : {'id' : '1'}, 'body' : json.dumps({'name' : 'Updated', 'price': 1.99, 'description': 'Test Item Description'})}
        
        response = lambda_handler(event,None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(body["error"], "Active Item with ID 1 not found")

    @patch("api.items.update_item.update_item.get_db_connection")
    def test_lambda_handler_update_item_throws_error_when_db_throws_error(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, side_effect=psycopg2.Error)

        event = {'pathParameters' : {'id' : '1'}, 'body' : json.dumps({'name' : 'Updated', 'price': 1.99, 'description': 'Test Item Description'})}

        response = lambda_handler(event,None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(body["error"], "Database error")

    @patch("api.items.update_item.update_item.get_db_connection")
    def test_lambda_handler_update_item_throws_error_when_db_throws_exception(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, side_effect=Exception)

        event = {'pathParameters' : {'id' : '1'}, 'body' : json.dumps({'name' : 'Updated', 'price': 1.99, 'description': 'Test Item Description'})}

        response = lambda_handler(event,None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(body["error"], "Internal server error")