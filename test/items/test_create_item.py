import unittest
import psycopg2
from unittest.mock import MagicMock, patch
import json
from api.items.create_item.create_item import lambda_handler
from test.helper_funcs.setup_mock_db import setup_mock_db
import datetime

class TestCreateItem(unittest.TestCase):
    def setUp(self):
        self.mock_description = [
            ("id",), ("name",), ("price",), ("description",), ("created_at",)
        ]

    @patch("api.items.create_item.create_item.get_db_connection")
    def test_lambda_handler_creates_expected_item(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchone=(1, datetime.datetime(2025, 7, 2, 12, 0, 0)), description=self.mock_description)

        event = {'body' : json.dumps({'name' : 'Created', 'price' : 1.99, 'description': 'Created iteam'})}
        expectedResponseBody = {'id': 1, 'name' : 'Created', 'price' : 1.99, 'description': 'Created iteam', 'created_at': '2025-07-02 12:00:00'}

        response = lambda_handler(event,None)

        self.assertEqual(response['statusCode'], 201)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)

    @patch("api.items.create_item.create_item.get_db_connection")
    def test_lambda_handler_create_item_runs_with_description_missing(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchone=(1, datetime.datetime(2025, 7, 2, 12, 0, 0)), description=self.mock_description)

        event = {'body' : json.dumps({'name' : 'Created', 'price' : 1.99})}
        expectedResponseBody = {'id': 1, 'name' : 'Created', 'price' : 1.99, 'description': None, 'created_at': '2025-07-02 12:00:00'}

        response = lambda_handler(event,None)

        self.assertEqual(response['statusCode'], 201)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)

    def test_lambda_handler_create_item_throws_error_with_name_missing(self):
        event = {'body' : json.dumps({'price' : 1.99, 'description': 'Created iteam'})}

        response = lambda_handler(event,None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Invalid request data")

    def test_lambda_handler_create_item_throws_error_with_price_missing(self):
        event = {'body' : json.dumps({'name' : 'Created', 'description': 'Created iteam'})}

        response = lambda_handler(event,None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Invalid request data")

    def test_lambda_handler_create_item_throws_error_with_string_price(self):
        event = {'body' : json.dumps({'' : 'Created', 'price' : 'One Pound', 'description': 'Created iteam'})}

        response = lambda_handler(event,None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Invalid request data")

    def test_lambda_handler_create_item_throws_error_with_body_as_string(self):
        event = {'body' : 'id: 1, name : Created, price : 1.99, description: Created iteam'}

        response = lambda_handler(event,None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Invalid request data")

    def test_lambda_handler_create_item_throws_error_with_missing_body(self):
        response = lambda_handler({},None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Invalid request data")

    @patch("api.items.create_item.create_item.get_db_connection")
    def test_lambda_handler_create_item_throws_error_when_db_has_error(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, side_effect=psycopg2.Error)

        event = {'body' : json.dumps({'name' : 'Created', 'price' : 1.99, 'description': 'Created iteam'})}

        response = lambda_handler(event,None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(body["error"], "Database error")
