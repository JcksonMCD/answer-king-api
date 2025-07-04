import unittest
import psycopg2
from unittest.mock import MagicMock, patch
import json
from api.categories.update_category.update_category import lambda_handler, json_default
from test.helper_funcs.setup_mock_db import setup_mock_db
import datetime

class TestUpdateCategory(unittest.TestCase):
    def setUp(self):
        self.mock_description = [
            ("id",), ("name",), ("created_at",)
        ]

    @patch("api.categories.update_category.update_category.get_db_connection")
    def test_lambda_handler_updates_expected_category(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchone=(1, "Updated"), description=self.mock_description)

        event = {'pathParameters' : {'id' : '1'}, 'body' : json.dumps({'name' : 'Updated'})}
        expectedResponseBody = {'id': 1, 'name': 'Updated'}

        response = lambda_handler(event,None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)

    def test_lambda_handler_update_category_throws_error_with_incorrect_path(self):
        event = {'pathParameters' : {'id' : ''}, 'body' : json.dumps({'name' : 'Updated'})}

        response = lambda_handler(event,None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Invalid or missing ID in path or request data")

    def test_lambda_handler_update_category_throws_error_with_missing_path(self):
        event = {'body' : json.dumps({'name' : 'Updated'})}

        response = lambda_handler(event,None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Invalid or missing ID in path or request data")

    def test_lambda_handler_update_category_throws_error_with_incorrect_body(self):
        event = {'pathParameters' : {'id' : '1'}, 'body' : json.dumps({'' : 'Updated'})}

        response = lambda_handler(event,None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Invalid or missing ID in path or request data")

    def test_lambda_handler_update_category_throws_error_with_missing_body(self):
        event = {'pathParameters' : {'id' : '1'}}

        response = lambda_handler(event,None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Invalid or missing ID in path or request data")

    @patch("api.categories.update_category.update_category.get_db_connection")
    def test_lambda_handler_update_category_throws_error_if_row_not_returned(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchone=())

        event = {'pathParameters' : {'id' : '1'}, 'body' : json.dumps({'name' : 'Updated'})}
        
        response = lambda_handler(event,None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(body["error"], "No active Category not found at ID: 1")

    @patch("api.categories.update_category.update_category.get_db_connection")
    def test_lambda_handler_update_category_throws_error_when_db_has_error(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, side_effect=psycopg2.Error)

        event = {'pathParameters' : {'id' : '1'}, 'body' : json.dumps({'name' : 'Updated'})}

        response = lambda_handler(event,None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(body["error"], "Database error")

    def test_default_json_handles_datetime(self):
        dateObj = datetime.datetime(2025, 7, 2)
        self.assertEqual(dateObj.isoformat(), json_default(dateObj))

    def test_default_json_handles_string(self):
        stringObj = "String Object"
        self.assertEqual("String Object", json_default(stringObj))

    def test_default_json_handles_float(self):
        floatObj = 1.99
        self.assertEqual("1.99", json_default(floatObj))
