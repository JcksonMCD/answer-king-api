import unittest
import psycopg2
from unittest.mock import patch
import json
from api.categories.remove_category.remove_category import lambda_handler
from test.helper_funcs.setup_mock_db import setup_mock_db

class TestRemoveCategory(unittest.TestCase):

    @patch("api.categories.remove_category.remove_category.get_db_connection")
    def test_lambda_handler_removes_expected_category(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchone=(1,))

        event = {'pathParameters' : {'id' : '1'}}

        response = lambda_handler(event,None)

        self.assertEqual(response['statusCode'], 204)

    @patch("api.categories.remove_category.remove_category.get_db_connection")
    def test_lambda_handler_throws_error_when_db_errors(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, side_effect=psycopg2.Error)

        event = {'pathParameters' : {'id' : '1'}}
        expectedResponseBody = {'error': 'Database error'}

        response = lambda_handler(event,None)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)

    @patch("api.categories.remove_category.remove_category.get_db_connection")
    def test_lambda_handler_throws_error_when_db_returns_nothing(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchone=())

        event = {'pathParameters' : {'id' : '1'}}
        expectedResponseBody = {'error': 'Category with ID 1 not found'}

        response = lambda_handler(event,None)

        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)



