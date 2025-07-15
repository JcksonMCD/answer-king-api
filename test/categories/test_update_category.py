import unittest
import psycopg2
from unittest.mock import patch
import json
from api.categories.update_category.update_category import lambda_handler
from test.helper_funcs.setup_mock_db import setup_mock_db

class TestUpdateCategory(unittest.TestCase):

    @patch("api.categories.update_category.update_category.get_db_connection")
    def test_lambda_handler_updates_expected_category(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchone={'id': 1, 'name': 'Updated'})

        event = {'pathParameters' : {'id' : '1'}, 'body' : json.dumps({'name' : 'Updated'})}
        expectedResponseBody = {'id': 1, 'name': 'Updated'}

        response = lambda_handler(event,None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)

    @patch("api.categories.update_category.update_category.get_db_connection")
    def test_lambda_handler_update_category_throws_error_if_row_not_returned(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchone={})

        event = {'pathParameters' : {'id' : '1'}, 'body' : json.dumps({'name' : 'Updated'})}
        
        response = lambda_handler(event,None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(body["error"], "Category with ID 1 not found")

    @patch("api.categories.update_category.update_category.get_db_connection")
    def test_lambda_handler_update_category_throws_error_when_db_throws_error(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, side_effect=psycopg2.Error)

        event = {'pathParameters' : {'id' : '1'}, 'body' : json.dumps({'name' : 'Updated'})}

        response = lambda_handler(event,None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(body["error"], "Database error")

    @patch("api.categories.update_category.update_category.get_db_connection")
    def test_lambda_handler_update_category_throws_error_when_db_throws_exception(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, side_effect=Exception)

        event = {'pathParameters' : {'id' : '1'}, 'body' : json.dumps({'name' : 'Updated'})}

        response = lambda_handler(event,None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(body["error"], "Internal server error")