import json
import unittest
import psycopg2
from unittest.mock import patch, MagicMock, Mock
from test.helper_funcs.setup_mock_db import setup_mock_db
from api.item_categories.get_items_by_category.get_items_by_category import validate_category_exists, fetch_items_by_category_from_db, lambda_handler

class TestGetItemsByCategory(unittest.TestCase):
    def setUp(self):
        self.mock_cursor = Mock()
        self.mock_description = [
            ("id",), ("name",), ("price",)
        ]

    @patch('api.item_categories.get_items_by_category.get_items_by_category.get_active_row_from_table')
    def test_validate_category_exist_returns_none_when_entities_exists(self, mock_get_active_row):
        mock_get_active_row.side_effect = (1, 'Category')
        
        response = validate_category_exists(self.mock_cursor, 1)
        
        self.assertIsNone(response)
        mock_get_active_row.assert_called_once_with(self.mock_cursor, table_name='categories', id=1)
    
    @patch('api.item_categories.get_items_by_category.get_items_by_category.get_active_row_from_table')
    def test_validate_category_exist_throws_error_with_no_active_category(self, mock_get_active_row):
        mock_get_active_row.return_value = ()
        
        response = validate_category_exists(self.mock_cursor, 1)
        expected_response = {'statusCode': 400, 'body': json.dumps({'error' : f'No Active Category found at ID: 1'})}
        
        self.assertEqual(response, expected_response)
        mock_get_active_row.assert_called_once_with(self.mock_cursor, table_name='categories', id=1)

    @patch('api.item_categories.get_items_by_category.get_items_by_category.get_db_connection')
    @patch('api.item_categories.get_items_by_category.get_items_by_category.validate_category_exists')
    def test_fetch_items_by_category_in_db_returns_success_json(self, mock_validate_category, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchall=[
            (1, "Test Item", 1.99, "Test Item Description")
        ], description=self.mock_description)

        mock_validate_category.return_value = None
        expectedResponseBody = [{'id': 1, 'name': 'Test Item', 'price': 1.99}]

        response = fetch_items_by_category_from_db(1)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), expectedResponseBody)
        mock_validate_category.assert_called_once()

    @patch('api.item_categories.get_items_by_category.get_items_by_category.get_db_connection')
    @patch('api.item_categories.get_items_by_category.get_items_by_category.validate_category_exists')
    def test_fetch_items_by_category_in_db_returns_empty_list_when_no_items(self, mock_validate_category, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection, fetchall=[], description=self.mock_description)

        mock_validate_category.return_value = None
        response = fetch_items_by_category_from_db(1)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), [])
        mock_validate_category.assert_called_once()

    @patch('api.item_categories.get_items_by_category.get_items_by_category.get_db_connection')
    @patch('api.item_categories.get_items_by_category.get_items_by_category.validate_category_exists')
    def test_fetch_items_by_category_in_db_returns_error_for_no_active_category(self, mock_validate_category, mock_get_db_connection):
        setup_mock_db(mock_get_db_connection)
        mock_validate_category.return_value = {'statusCode': 400, 'body': json.dumps({'error' : 'No Active Category found at ID: 1'})}

        response = fetch_items_by_category_from_db(1)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body']), {'error': 'No Active Category found at ID: 1'})
        mock_validate_category.assert_called_once()

    @patch('api.item_categories.get_items_by_category.get_items_by_category.get_db_connection')
    def test_fetch_item_to_category_returns_psycopg2_error_json(self, mock_get_db_connection):
        mock_get_db_connection.return_value.__enter__.side_effect = psycopg2.Error

        response = fetch_items_by_category_from_db(1)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body']), {'error': 'Database error'})

    @patch('api.item_categories.get_items_by_category.get_items_by_category.get_db_connection')
    def test_fetch_item_to_category_returns_exception_json(self, mock_get_db_connection):
        mock_get_db_connection.return_value.__enter__.side_effect = Exception

        response = fetch_items_by_category_from_db(1)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body']), {'error': 'Internal server error'})
   
    @patch('api.item_categories.get_items_by_category.get_items_by_category.extract_id')
    def test_lambda_handler_returns_exception_json(self, mock_extract_id):
        mock_extract_id.side_effect = Exception

        response = lambda_handler({'pathParameters' : {'id' : '1'}}, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body']), {'error': 'Internal server error'})

    @patch('api.item_categories.get_items_by_category.get_items_by_category.extract_id')
    def test_lambda_handler_returns_validation_error_json(self, mock_extract_id):
        mock_extract_id.return_value = {'statusCode': 400, 'body': json.dumps({'error': 'Invalid or missing ID in path'})}

        response = lambda_handler({}, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body']), {'error': 'Invalid or missing ID in path'})

    @patch('api.item_categories.get_items_by_category.get_items_by_category.extract_id')
    @patch('api.item_categories.get_items_by_category.get_items_by_category.fetch_items_by_category_from_db')
    def test_lambda_handler_success(self, mock_fetch_items_by_category_from_db, mock_extract_id):
        mock_extract_id.return_value = (1, 2)
        mock_fetch_items_by_category_from_db.return_value = {'statusCode': 200, 'body': json.dumps({'id': 1, 'name': 'Test Item', 'price': 1.99})}

        response = lambda_handler({'pathParameters' : {'id' : '1'}}, None)

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(json.loads(response['body']), {'id': 1, 'name': 'Test Item', 'price': 1.99})

    @patch('api.item_categories.get_items_by_category.get_items_by_category.extract_id')
    @patch('api.item_categories.get_items_by_category.get_items_by_category.fetch_items_by_category_from_db')
    def test_lambda_handler_with_fetch_error(self, mock_fetch_items_by_category_from_db, mock_extract_id):
        mock_extract_id.return_value = 1
        
        mock_fetch_items_by_category_from_db.return_value = {
            'statusCode': 500, 
            'body': json.dumps({'error': 'Database error'})
        }

        response = lambda_handler({'pathParameters': {'id': '1'}}, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body']), {'error': 'Database error'})
        mock_extract_id.assert_called_once()
        mock_fetch_items_by_category_from_db.assert_called_once_with(1)

