import json
import unittest
import psycopg2
from unittest.mock import patch, Mock
from test.helper_funcs.setup_mock_db import setup_mock_db
from api.item_categories.get_items_by_category.get_items_by_category import fetch_items_by_category_from_db, lambda_handler
from api.lambda_layers.utils.python.utils.custom_exceptions import ValidationError, ActiveResourceNotFoundError

class TestGetItemsByCategory(unittest.TestCase):

    @patch('api.item_categories.get_items_by_category.get_items_by_category.get_db_connection')
    @patch('api.item_categories.get_items_by_category.get_items_by_category.get_active_row_from_table')
    def test_fetch_items_by_category_in_db_returns_success_json(self, mock_get_active_row, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchall=[{'id': 1, 'name': 'Test Item', 'price': 1.99}])

        mock_get_active_row.return_value = None

        expected = [{'id': 1, 'name': 'Test Item', 'price': 1.99}]
        result = fetch_items_by_category_from_db(1)

        self.assertEqual(result, expected)

    @patch('api.item_categories.get_items_by_category.get_items_by_category.get_db_connection')
    @patch('api.item_categories.get_items_by_category.get_items_by_category.get_active_row_from_table')
    def test_fetch_items_by_category_returns_empty_list(self, mock_get_active_row, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchall=[])
        mock_get_active_row.return_value = None

        result = fetch_items_by_category_from_db(1)
        self.assertEqual(result, [])

    @patch('api.item_categories.get_items_by_category.get_items_by_category.get_db_connection')
    @patch('api.item_categories.get_items_by_category.get_items_by_category.get_active_row_from_table')
    def test_fetch_items_by_category_raises_on_missing_category(self, mock_get_active_row, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection)
        mock_get_active_row.side_effect = ActiveResourceNotFoundError("Category not found", 404)

        with self.assertRaises(ActiveResourceNotFoundError):
            fetch_items_by_category_from_db(1)

    @patch('api.item_categories.get_items_by_category.get_items_by_category.get_db_connection')
    def test_fetch_items_by_category_raises_psycopg2_error(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, side_effect=psycopg2.Error)

        with self.assertRaises(psycopg2.Error):
            fetch_items_by_category_from_db(1)

    @patch('api.item_categories.get_items_by_category.get_items_by_category.get_db_connection')
    def test_fetch_items_by_category_raises_generic_exception(self, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, side_effect=Exception("Unexpected"))

        with self.assertRaises(Exception):
            fetch_items_by_category_from_db(1)

    @patch('api.item_categories.get_items_by_category.get_items_by_category.fetch_items_by_category_from_db')
    @patch('api.item_categories.get_items_by_category.get_items_by_category.extract_id_path_param')
    def test_lambda_handler_success(self, mock_extract_id, mock_fetch_items):
        mock_extract_id.return_value = 1
        mock_fetch_items.return_value = [{'id': 1, 'name': 'Test Item', 'price': 1.99}]

        response = lambda_handler({'pathParameters': {'id': '1'}}, None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), [{'id': 1, 'name': 'Test Item', 'price': 1.99}])
   
    @patch('api.item_categories.get_items_by_category.get_items_by_category.fetch_items_by_category_from_db')
    def test_lambda_handler_validation_error_invalid_id(self, mock_fetch_items):
        event = {'pathParameters': {'id': 'not_an_int'}}
        context = {}
        
        response = lambda_handler(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['error'] == 'ID must be an integer'
        mock_fetch_items.assert_not_called()

    @patch('api.item_categories.get_items_by_category.get_items_by_category.fetch_items_by_category_from_db')
    def test_lambda_handler_validation_error_missing_id(self, mock_fetch_items):
        event = {'pathParameters': {}}
        context = {}
        
        response = lambda_handler(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['error'] == 'Invalid or missing path ID'
        mock_fetch_items.assert_not_called()

    @patch('api.item_categories.get_items_by_category.get_items_by_category.fetch_items_by_category_from_db')
    def test_lambda_handler_validation_error_no_path_params(self, mock_fetch_items):
        event = {}
        context = {}
        
        response = lambda_handler(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['error'] == 'Invalid or missing path ID'
        mock_fetch_items.assert_not_called()

    @patch('api.item_categories.get_items_by_category.get_items_by_category.extract_id_path_param')
    @patch('api.item_categories.get_items_by_category.get_items_by_category.fetch_items_by_category_from_db')
    def test_lambda_handler_db_error(self, mock_fetch, mock_extract_id):
        mock_extract_id.return_value = 1
        mock_fetch.side_effect = psycopg2.Error("Database down")

        response = lambda_handler({'pathParameters': {'id': '1'}}, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body']), {'error': 'Database error'})

    @patch('api.item_categories.get_items_by_category.get_items_by_category.extract_id_path_param')
    @patch('api.item_categories.get_items_by_category.get_items_by_category.fetch_items_by_category_from_db')
    def test_lambda_handler_unexpected_error(self, mock_fetch, mock_extract_id):
        mock_extract_id.return_value = 1
        mock_fetch.side_effect = Exception("Unexpected failure")

        response = lambda_handler({'pathParameters': {'id': '1'}}, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body']), {'error': 'Internal server error'})
