import unittest
import psycopg2
from unittest.mock import MagicMock, patch
import json
from api.categories.get_all_categories.get_all_categories import lambda_handler
from test.helper_funcs.setup_mock_db import setup_mock_db
import datetime

class TestGetAllCategories(unittest.TestCase):
    def setUp(self):
        self.mock_description = [
            ("id",), ("name",), ("created_at",)
        ]

    @patch("api.categories.get_all_categories.get_all_categories.get_db_connection")
    def test_lambda_handler_returns_expected_category(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchall=[(1, "Test Category", datetime.datetime(2025, 7, 2, 12, 0, 0))], description=self.mock_description)

        expectedResponseBody = [{'id': 1, 'name': 'Test Category', 'created_at': '2025-07-02T12:00:00'}]

        response = lambda_handler({},None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)

    @patch("api.categories.get_all_categories.get_all_categories.get_db_connection")
    def test_lambda_handler_returns_expected_categories(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchall=[(1, "Test Category", datetime.datetime(2025, 7, 2, 12, 0, 0)), (2, "Test Category 2", datetime.datetime(2025, 7, 2, 12, 0, 0))], description=self.mock_description)

        expectedResponseBody = [{'id': 1, 'name': 'Test Category', 'created_at': '2025-07-02T12:00:00'}, {'id': 2, 'name': 'Test Category 2', 'created_at': '2025-07-02T12:00:00'}]

        response = lambda_handler({},None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)

    @patch("api.categories.get_all_categories.get_all_categories.get_db_connection")
    def test_lambda_handler_returns_empty_list_if_empty_db_return(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchall=[], description=self.mock_description)

        expectedResponseBody = []

        response = lambda_handler({},None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)

    @patch("api.categories.get_all_categories.get_all_categories.get_db_connection")
    def test_lambda_handler_throws_database_error(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, side_effect=psycopg2.Error)

        response = lambda_handler({},None)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(body, {'error': 'Database error'})
