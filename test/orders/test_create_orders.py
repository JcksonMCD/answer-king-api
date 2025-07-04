import unittest
import psycopg2
from unittest.mock import patch
import json
from api.orders.create_order.create_order import lambda_handler
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

        expectedResponseBody = {'id' : 1, 'status' : 'pending', 'total': '0', 'created_at': '2025-07-02T12:00:00'}

        response = lambda_handler({},None)

        self.assertEqual(response['statusCode'], 201)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)

    @patch("api.orders.create_order.create_order.get_db_connection")
    def test_lambda_handler_creates_expected_order_and_ignores_any_event_body(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchone=(1, 'pending', 0, datetime.datetime(2025, 7, 2, 12, 0, 0)), description=self.mock_description)

        event = {'body' : json.dumps({'total': 10})}
        expectedResponseBody = {'id' : 1, 'status' : 'pending', 'total': '0', 'created_at': '2025-07-02T12:00:00'}

        response = lambda_handler(event,None)

        self.assertEqual(response['statusCode'], 201)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)

    @patch("api.orders.create_order.create_order.get_db_connection")
    def test_lambda_handler_create_order_throws_error_when_db_has_error(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchone=(), side_effect=psycopg2.Error)

        response = lambda_handler({},None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(body["error"], "Database error")

    @patch("api.orders.create_order.create_order.get_db_connection")
    def test_lambda_handler_handles_db_returning_none(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchone=None)

        response = lambda_handler({}, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body'])["error"], 'No data returned from DB')