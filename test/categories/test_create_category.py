import unittest
import psycopg2
from unittest.mock import patch
import json
from api.categories.create_category.create_category import lambda_handler
from test.helper_funcs.setup_mock_db import setup_mock_db
import datetime

class TestCreateCategory(unittest.TestCase):
    def setUp(self):
        self.mock_description = [
            ("id",), ("name",), ("created_at",)
        ]

    @patch("api.categories.create_category.create_category.get_db_connection")
    def test_lambda_handler_creates_expected_category(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, 
                           fetchone=(1, 'Created', datetime.datetime(2025, 7, 2, 12, 0, 0)),
                           description=self.mock_description)

        event = {'body' : json.dumps({'name' : 'Created'})}
        expectedResponseBody = {'id': 1, 'name': 'Created', 'created_at': '2025-07-02T12:00:00'}

        response = lambda_handler(event,None)

        self.assertEqual(response['statusCode'], 201)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)

    @patch("api.categories.create_category.create_category.get_db_connection")
    def test_lambda_handler_create_category_throws_error_when_db_has_error(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, side_effect=psycopg2.Error)

        event = {'body' : json.dumps({'name' : 'Created'})}

        response = lambda_handler(event,None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(body["error"], "Database error")

    @patch("api.categories.create_category.create_category.get_db_connection")
    def test_lambda_handler_create_category_throws_error_when_db_has_exception(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, side_effect=Exception)

        event = {'body' : json.dumps({'name' : 'Created'})}

        response = lambda_handler(event,None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(body["error"], "Internal server error")
