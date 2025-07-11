import unittest
import psycopg2
from unittest.mock import patch
import json
from api.items.get_all_items.get_all_items import lambda_handler, json_default
from test.helper_funcs.setup_mock_db import setup_mock_db
import datetime

class TestGetAllItems(unittest.TestCase):
    def setUp(self):
        self.mock_description = [
            ("id",), ("name",), ("price",), ("description",), ("created_at",)
        ]

    @patch("api.items.get_all_items.get_all_items.get_db_connection")
    def test_lambda_handler_returns_expected_item(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchall=[
            (1, "Test Item", 1.99, "Test Item Description", datetime.datetime(2025, 7, 2, 12, 0, 0))
        ], description=self.mock_description)

        expectedResponseBody = [{'id': 1, 'name': 'Test Item', 'price': 1.99, 'description': 'Test Item Description', 'created_at': '2025-07-02T12:00:00'}]

        response = lambda_handler({},None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)

    @patch("api.items.get_all_items.get_all_items.get_db_connection")
    def test_lambda_handler_returns_expected_items(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchall=[(1, "Test Item", 1.99, "Test Item Description", datetime.datetime(2025, 7, 2, 12, 0, 0)),
                                                        (2, "Test Item 2", 2.99, "Test Item 2 Description", datetime.datetime(2025, 7, 2, 12, 0, 0))
                                                        ],description=self.mock_description)

        expectedResponseBody = [{'id': 1, 'name': 'Test Item', 'price': 1.99, 'description': 'Test Item Description', 'created_at': '2025-07-02T12:00:00'}, 
                                {'id': 2, 'name': 'Test Item 2', 'price': 2.99, 'description': 'Test Item 2 Description', 'created_at': '2025-07-02T12:00:00'}]

        response = lambda_handler({},None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)

    @patch("api.items.get_all_items.get_all_items.get_db_connection")
    def test_lambda_handler_returns_empty_list_if_empty_db_return(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchall={}, description=self.mock_description)

        expectedResponseBody = []

        response = lambda_handler({},None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)

    @patch("api.items.get_all_items.get_all_items.get_db_connection")
    def test_lambda_handler_throws_database_error(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, side_effect = psycopg2.Error('DB Error'))

        response = lambda_handler({},None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(body, {'error': 'Database error'})

    @patch("api.items.get_all_items.get_all_items.get_db_connection")
    def test_lambda_handler_throws_database_exception(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, side_effect = Exception)

        response = lambda_handler({},None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(body, {'error': 'Internal server error'})

    def test_default_json_handles_datetime(self):
        dateObj = datetime.datetime(2025, 7, 2)
        self.assertEqual(dateObj.isoformat(), json_default(dateObj))

    def test_default_json_handles_string(self):
        stringObj = "String Object"
        self.assertEqual("String Object", json_default(stringObj))

    def test_default_json_handles_float(self):
        floatObj = 1.99
        self.assertEqual("1.99", json_default(floatObj))