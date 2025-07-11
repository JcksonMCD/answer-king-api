import unittest
import psycopg2
from unittest.mock import patch
import json
from api.items.get_item_by_id.get_item_by_id import lambda_handler, json_default
from test.helper_funcs.setup_mock_db import setup_mock_db
import datetime

class TestGetItemByID(unittest.TestCase):
    def setUp(self):
        self.mock_description = [
            ("id",), ("name",), ("price",), ("description",), ("created_at",)
        ]

    @patch("api.items.get_item_by_id.get_item_by_id.get_db_connection")
    def test_lambda_handler_returns_expected_item(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchone=(1, "Test Item", 1.99, "Test Item Description", datetime.datetime(2025, 7, 2, 12, 0, 0)), description=self.mock_description)

        expectedResponseBody = {'id': 1, 'name': 'Test Item', 'price': 1.99, 'description': 'Test Item Description', 'created_at': '2025-07-02T12:00:00'}

        event = {'pathParameters' : {'id' : '1'}}
        response = lambda_handler(event,None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)

    @patch("api.items.get_item_by_id.get_item_by_id.get_db_connection")
    def test_lambda_handler_returns_expected_item_with_null_description(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchone=(1, "Test Item", 1.99, None, datetime.datetime(2025, 7, 2, 12, 0, 0)), description=self.mock_description)

        expectedResponseBody = {'id': 1, 'name': 'Test Item', 'price': 1.99, 'description': None, 'created_at': '2025-07-02T12:00:00'}

        event = {'pathParameters' : {'id' : '1'}}
        response = lambda_handler(event,None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)


    @patch("api.items.get_item_by_id.get_item_by_id.get_db_connection")
    def test_lambda_handler_throws_error_if_no_item_found(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection,fetchone=())

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

    def test_default_json_handles_string(self):
        self.assertEqual("String Object", json_default("String Object"))

    def test_default_json_handles_float(self):
        self.assertEqual("1.99", json_default(1.99))
    
    def test_default_json_handles_datetime(self):
        dateObj = datetime.datetime(2025, 7, 2)
        self.assertEqual(dateObj.isoformat(), json_default(dateObj))