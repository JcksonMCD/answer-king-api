import unittest
import psycopg2
from unittest.mock import patch
import json
from api.items.remove_item.remove_item import lambda_handler
from test.helper_funcs.setup_mock_db import setup_mock_db

class TestRemoveItem(unittest.TestCase):
    def setUp(self):
        self.mock_description = [
            ("id",), ("name",), ("price",), ("description",), ("created_at",)
        ]

    @patch("api.items.remove_item.remove_item.get_db_connection")
    def test_lambda_handler_removes_expected_item(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchone=(1,), description=self.mock_description)

        event = {'pathParameters' : {'id' : '1'}}
        expectedResponseBody = {'deleted_id': 1}

        response = lambda_handler(event,None)

        self.assertEqual(response['statusCode'], 204)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)

    @patch("api.items.remove_item.remove_item.get_db_connection")
    def test_lambda_handler_throws_error_when_db_errors(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, side_effect=psycopg2.Error)

        event = {'pathParameters' : {'id' : '1'}}
        expectedResponseBody = {'error': 'Database error'}

        response = lambda_handler(event,None)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)

    @patch("api.items.remove_item.remove_item.get_db_connection")
    def test_lambda_handler_throws_error_when_db_throws_exception(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, side_effect=Exception)

        event = {'pathParameters' : {'id' : '1'}}
        expectedResponseBody = {'error': 'Internal server error'}

        response = lambda_handler(event,None)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)

    @patch("api.items.remove_item.remove_item.get_db_connection")
    def test_lambda_handler_throws_error_when_db_returns_nothing(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchone=())

        event = {'pathParameters' : {'id' : '1'}}
        expectedResponseBody = {'error': 'Item not found at ID: 1'}

        response = lambda_handler(event,None)

        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)



