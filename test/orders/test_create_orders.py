import unittest
import psycopg2
from unittest.mock import patch
import json
from api.orders.create_order.create_order import lambda_handler, post_order_to_db
from test.helper_funcs.setup_mock_db import setup_mock_db
import datetime

class TestCreateOrder(unittest.TestCase):
    def setUp(self):
        self.mock_description = [
            ("id",), ("status",), ("total",), ("created_at",)
        ]

    @patch("api.orders.create_order.create_order.get_db_connection")
    def test_lambda_handler_creates_expected_order(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchone=(1, 'pending', 0, datetime.datetime(2025, 7, 2, 12, 0, 0)), description=self.mock_description)

        expectedResponseBody = {'id' : 1, 'status' : 'pending', 'total': 0, 'created_at': '2025-07-02T12:00:00'}

        response = lambda_handler({}, None)

        self.assertEqual(response['statusCode'], 200)  
        self.assertEqual(json.loads(response['body']), expectedResponseBody)

    @patch("api.orders.create_order.create_order.get_db_connection")
    def test_lambda_handler_creates_expected_order_and_ignores_any_event_body(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchone=(1, 'pending', 0, datetime.datetime(2025, 7, 2, 12, 0, 0)), description=self.mock_description)

        event = {'body' : json.dumps({'total': 10})}
        expectedResponseBody = {'id' : 1, 'status' : 'pending', 'total': 0, 'created_at': '2025-07-02T12:00:00'}

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 200) 
        self.assertEqual(json.loads(response['body']), expectedResponseBody)

    @patch("api.orders.create_order.create_order.get_db_connection")
    def test_lambda_handler_create_order_throws_error_when_db_has_error(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchone=(), side_effect=psycopg2.Error)

        response = lambda_handler({}, None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(body["error"], "Database error")

    @patch("api.orders.create_order.create_order.get_db_connection")
    def test_lambda_handler_handles_db_returning_none(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchone=None)

        response = lambda_handler({}, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body'])["error"], 'Failed to create order')

    @patch("api.orders.create_order.create_order.get_db_connection")
    def test_lambda_handler_handles_unexpected_exception(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchone=(), side_effect=Exception("Unexpected error"))

        response = lambda_handler({}, None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(body["error"], "Internal server error")

    @patch("api.orders.create_order.create_order.get_db_connection")
    def test_lambda_handler_creates_order_with_different_data_types(self, mock_get_db_connection):
        setup_mock_db(
            mock_get_db_connection, 
            fetchone=(999, 'completed', 25.50, datetime.datetime(2025, 12, 31, 23, 59, 59)), 
            description=self.mock_description
        )

        expectedResponseBody = {
            'id': 999, 
            'status': 'completed', 
            'total': 25.50, 
            'created_at': '2025-12-31T23:59:59'
        }

        response = lambda_handler({}, None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)

    @patch("api.orders.create_order.create_order.get_db_connection")
    def test_lambda_handler_handles_connection_error(self, mock_get_db_connection):
        mock_get_db_connection.side_effect = psycopg2.OperationalError("Connection failed")

        response = lambda_handler({}, None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(body["error"], "Database error")

    @patch("api.orders.create_order.create_order.get_db_connection")
    def test_post_order_to_db_handles_no_result_returned(self, mock_get_db_connection):
        from api.orders.create_order.create_order import post_order_to_db
        
        setup_mock_db(mock_get_db_connection, fetchone=None)

        result = post_order_to_db()
        body = json.loads(result['body'])
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['statusCode'], 500)
        self.assertEqual(body['error'], 'Failed to create order')

    @patch("api.orders.create_order.create_order.get_db_connection")
    def test_post_order_to_db_handles_psycopg2_error(self, mock_get_db_connection):
        from api.orders.create_order.create_order import post_order_to_db
        
        setup_mock_db(mock_get_db_connection, side_effect=psycopg2.Error("Database connection failed"))

        result = post_order_to_db()
        body = json.loads(result['body'])
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['statusCode'], 500)
        self.assertEqual(body['error'], 'Database error')

    @patch("api.orders.create_order.create_order.get_db_connection")
    def test_post_order_to_db_handles_unexpected_exception(self, mock_get_db_connection):
        from api.orders.create_order.create_order import post_order_to_db
        
        setup_mock_db(mock_get_db_connection, side_effect=Exception("Unexpected error"))

        result = post_order_to_db()
        body = json.loads(result['body'])
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['statusCode'], 500)
        self.assertEqual(body['error'], 'Internal server error')