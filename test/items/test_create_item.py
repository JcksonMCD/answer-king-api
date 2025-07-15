import unittest
import psycopg2
from unittest.mock import patch
import json
from api.items.create_item.create_item import lambda_handler
from test.helper_funcs.setup_mock_db import setup_mock_db
import datetime

class TestCreateItem(unittest.TestCase):

    @patch("api.items.create_item.create_item.get_db_connection")
    def test_lambda_handler_creates_expected_item(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchone={'id': 1, 'name' : 'Created', 'price' : 1.99, 'description': 'Created iteam', 'created_at': '2025-07-02T12:00:00'})

        event = {'body' : json.dumps({'name' : 'Created', 'price' : 1.99, 'description': 'Created iteam'})}
        expectedResponseBody = {'id': 1, 'name' : 'Created', 'price' : 1.99, 'description': 'Created iteam', 'created_at': '2025-07-02T12:00:00'}

        response = lambda_handler(event,None)

        self.assertEqual(response['statusCode'], 201)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)

    @patch("api.items.create_item.create_item.get_db_connection")
    def test_lambda_handler_create_item_runs_with_description_missing(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, {'id': 1, 'name' : 'Created', 'price' : 1.99, 'description': None, 'created_at': '2025-07-02T12:00:00'})

        event = {'body' : json.dumps({'name' : 'Created', 'price' : 1.99})}
        expectedResponseBody = {'id': 1, 'name' : 'Created', 'price' : 1.99, 'description': None, 'created_at': '2025-07-02T12:00:00'}

        response = lambda_handler(event,None)

        self.assertEqual(response['statusCode'], 201)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)

    @patch("api.items.create_item.create_item.get_db_connection")
    def test_lambda_handler_create_item_throws_error_when_db_has_error(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, side_effect=psycopg2.Error)

        event = {'body' : json.dumps({'name' : 'Created', 'price' : 1.99, 'description': 'Created iteam'})}

        response = lambda_handler(event,None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(body["error"], "Database error")
    
    @patch("api.items.create_item.create_item.get_db_connection")
    def test_lambda_handler_create_item_throws_error_when_db_returns_nothing(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchone={})

        event = {'body' : json.dumps({'name' : 'Created', 'price' : 1.99, 'description': 'Created iteam'})}

        response = lambda_handler(event,None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Failed to insert item - no result returned")
