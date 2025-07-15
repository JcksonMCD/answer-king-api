import unittest
import psycopg2
from unittest.mock import patch
import json
from api.items.get_item_by_id.get_item_by_id import lambda_handler
from test.helper_funcs.setup_mock_db import setup_mock_db

class TestGetItemByID(unittest.TestCase):

    @patch("api.items.get_item_by_id.get_item_by_id.get_db_connection")
    def test_lambda_handler_returns_expected_item(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchone={'id': 1, 'name': 'Test Item', 'price': 1.99, 'description': 'Test Item Description', 'created_at': '2025-07-02T12:00:00'})

        expectedResponseBody = {'id': 1, 'name': 'Test Item', 'price': 1.99, 'description': 'Test Item Description', 'created_at': '2025-07-02T12:00:00'}

        event = {'pathParameters' : {'id' : '1'}}
        response = lambda_handler(event,None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)

    @patch("api.items.get_item_by_id.get_item_by_id.get_db_connection")
    def test_lambda_handler_returns_expected_item_with_null_description(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchone={'id': 1, 'name': 'Test Item', 'price': 1.99, 'description': None, 'created_at': '2025-07-02T12:00:00'})

        expectedResponseBody = {'id': 1, 'name': 'Test Item', 'price': 1.99, 'description': None, 'created_at': '2025-07-02T12:00:00'}

        event = {'pathParameters' : {'id' : '1'}}
        response = lambda_handler(event,None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)


    @patch("api.items.get_item_by_id.get_item_by_id.get_db_connection")
    def test_lambda_handler_throws_error_if_no_item_found(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection,fetchone={})

        event = {'pathParameters' : {'id' : '1'}}
        response = lambda_handler(event,None)

        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body']), {'error': 'Active Item with ID 1 not found'})

    @patch("api.items.get_item_by_id.get_item_by_id.get_db_connection")
    def test_lambda_handler_throws_database_error(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, side_effect=psycopg2.Error)

        event = {'pathParameters' : {'id' : '1'}}
        response = lambda_handler(event,None)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Database error', response['body'])

    @patch("api.items.get_item_by_id.get_item_by_id.get_db_connection")
    def test_lambda_handler_throws_error_when_exception_thrown(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, side_effect=Exception)

        event = {'pathParameters' : {'id' : '1'}}
        response = lambda_handler(event,None)

        self.assertEqual(response['statusCode'], 500)
        self.assertIn('Internal server error', response['body'])