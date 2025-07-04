import unittest
import psycopg2
from unittest.mock import MagicMock, patch
import json
from api.orders.create_order.create_order import lambda_handler
import datetime

class TestCreateOrder(unittest.TestCase):
    def setUp(self):
        self.mock_description = [
            ("id",), ("status",), ("total",), ("created_at",)
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

    @patch("api.orders.create_order.create_order.get_db_connection")
    def test_lambda_handler_creates_expected_order(self, mock_get_db_connection):
        self.setup_mock_db(mock_get_db_connection, fetchone=(1, 'pending', 0, datetime.datetime(2025, 7, 2, 12, 0, 0)))

        expectedResponseBody = {'id' : 1, 'status' : 'pending', 'total': '0', 'created_at': '2025-07-02T12:00:00'}

        response = lambda_handler({},None)

        self.assertEqual(response['statusCode'], 201)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)

    @patch("api.orders.create_order.create_order.get_db_connection")
    def test_lambda_handler_creates_expected_order_and_ignores_any_event_body(self, mock_get_db_connection):
        self.setup_mock_db(mock_get_db_connection, fetchone=(1, 'pending', 0, datetime.datetime(2025, 7, 2, 12, 0, 0)))

        event = {'body' : json.dumps({'total': 10})}
        expectedResponseBody = {'id' : 1, 'status' : 'pending', 'total': '0', 'created_at': '2025-07-02T12:00:00'}

        response = lambda_handler(event,None)

        self.assertEqual(response['statusCode'], 201)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)

    @patch("api.orders.create_order.create_order.get_db_connection")
    def test_lambda_handler_create_order_throws_error_when_db_has_error(self, mock_get_db_connection):
        self.setup_mock_db(mock_get_db_connection, side_effect=psycopg2.Error)

        response = lambda_handler({},None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(body["error"], "Database error")

    @patch("api.orders.create_order.create_order.get_db_connection")
    def test_lambda_handler_handles_db_returning_none(self, mock_get_db_connection):
        self.setup_mock_db(mock_get_db_connection, fetchone=None)

        response = lambda_handler({}, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body'])["error"], 'No data returned from DB')