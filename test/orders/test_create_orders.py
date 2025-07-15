import unittest
import psycopg2
from unittest.mock import patch
import json
import datetime
from api.orders.create_order.create_order import lambda_handler, post_order_to_db
from test.helper_funcs.setup_mock_db import setup_mock_db
from api.lambda_layers.utils.python.utils.custom_exceptions import DatabaseInsertError


class TestCreateOrder(unittest.TestCase):

    @patch("api.orders.create_order.create_order.get_db_connection")
    def test_lambda_handler_creates_expected_order(self, mock_get_db_connection):
        setup_mock_db(
            mock_get_db_connection,
            fetchone={'id': 1, 'status': 'pending', 'total': 0, 'created_at': '2025-07-02T12:00:00'},
        )

        expected = {'id': 1, 'status': 'pending', 'total': 0, 'created_at': '2025-07-02T12:00:00'}

        response = lambda_handler({}, None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), expected)

    @patch("api.orders.create_order.create_order.get_db_connection")
    def test_lambda_handler_ignores_event_body(self, mock_get_db_connection):
        setup_mock_db(
            mock_get_db_connection,
            fetchone={'id': 1, 'status': 'pending', 'total': 0, 'created_at': '2025-07-02T12:00:00'},
        )

        event = {'body': json.dumps({'total': 100})}
        expected = {'id': 1, 'status': 'pending', 'total': 0, 'created_at': '2025-07-02T12:00:00'}

        response = lambda_handler(event, None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), expected)

    @patch("api.orders.create_order.create_order.get_db_connection")
    def test_lambda_handler_handles_db_error(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, side_effect=psycopg2.Error)

        response = lambda_handler({}, None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(body["error"], "Database error")

    @patch("api.orders.create_order.create_order.get_db_connection")
    def test_lambda_handler_handles_none_result(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchone=None)

        response = lambda_handler({}, None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Failed to create order - no result returned")

    @patch("api.orders.create_order.create_order.get_db_connection")
    def test_lambda_handler_handles_unexpected_exception(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, side_effect=Exception("Unexpected error"))

        response = lambda_handler({}, None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(body["error"], "Internal server error")

    @patch("api.orders.create_order.create_order.get_db_connection")
    def test_lambda_handler_handles_different_data_types(self, mock_get_db_connection):
        setup_mock_db(
            mock_get_db_connection,
            fetchone={
            'id': 999,
            'status': 'completed',
            'total': 25.50,
            'created_at': '2025-12-31T23:59:59'
        },
        )

        expected = {
            'id': 999,
            'status': 'completed',
            'total': 25.50,
            'created_at': '2025-12-31T23:59:59'
        }

        response = lambda_handler({}, None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), expected)

    @patch("api.orders.create_order.create_order.get_db_connection")
    def test_lambda_handler_handles_connection_error(self, mock_get_db_connection):
        mock_get_db_connection.side_effect = psycopg2.OperationalError("Connection failed")

        response = lambda_handler({}, None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(body["error"], "Database error")

    @patch("api.orders.create_order.create_order.get_db_connection")
    def test_post_order_to_db_raises_error_when_result_none(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchone=None)

        with self.assertRaises(DatabaseInsertError):
            post_order_to_db()

    @patch("api.orders.create_order.create_order.get_db_connection")
    def test_post_order_to_db_raises_psycopg2_error(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, side_effect=psycopg2.Error("DB connection failed"))

        with self.assertRaises(psycopg2.Error):
            post_order_to_db()

    @patch("api.orders.create_order.create_order.get_db_connection")
    def test_post_order_to_db_raises_generic_exception(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, side_effect=Exception("Unexpected error"))

        with self.assertRaises(Exception) as context:
            post_order_to_db()

        self.assertEqual(str(context.exception), "Unexpected error")
