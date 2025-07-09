import json
import unittest
import psycopg2
from unittest.mock import patch, MagicMock, Mock
from test.helper_funcs.setup_mock_db import setup_mock_db
from api.item_categories.add_item_to_category.add_item_to_category import extract_and_validate_ids, validate_entities_exist, create_item_category_association, post_item_to_category_in_db, lambda_handler

class TestAddItemToCategory(unittest.TestCase):
    def setUp(self):
        self.mock_conn= MagicMock()
        self.mock_cursor = MagicMock()
    
    @patch('api.item_categories.add_item_to_category.add_item_to_category.extract_id', Mock(return_value=1))
    @patch('api.item_categories.add_item_to_category.add_item_to_category.extract_item_id', Mock(return_value=2))
    def test_extract_and_validate_id_returns_two_ids(self):
        event = {'pathParameters': {'id': 1}, 'queryStringParameters': {'itemID': 2}}

        response = extract_and_validate_ids(event)

        self.assertEqual(response, (1, 2))

    @patch('api.item_categories.add_item_to_category.add_item_to_category.extract_id')
    @patch('api.item_categories.add_item_to_category.add_item_to_category.extract_item_id', Mock(return_value=2))
    def test_extract_and_validate_id_returns_error_body_of_extract_id(self, mock_extract_id):
        error_response = {'statusCode': 400, 'body': {'error': 'Invalid or missing ID in path'}}
        mock_extract_id.return_value = error_response
        event = {'pathParameters': {'id': 1}, 'queryStringParameters': {'itemID': 2}}

        response = extract_and_validate_ids(event)

        self.assertEqual(response, error_response)

    @patch('api.item_categories.add_item_to_category.add_item_to_category.extract_id', Mock(return_value=1))
    @patch('api.item_categories.add_item_to_category.add_item_to_category.extract_item_id')
    def test_extract_and_validate_id_returns_error_body_of_extract_item_id(self, mock_extract_item_id):
        error_response = {'statusCode': 400, 'body': {'error': 'Invalid or missing ID in path. Must use query string parameter labeled itemID'}}
        mock_extract_item_id.return_value = error_response
        event = {'pathParameters': {'id': 1}, 'queryStringParameters': {'itemID': 2}}

        response = extract_and_validate_ids(event)

        self.assertEqual(response, error_response)

    @patch('api.item_categories.add_item_to_category.add_item_to_category.get_active_row_from_table')
    def test_validate_entities_exist_returns_none_when_entities_exist(self, mock_get_active_row):
        mock_get_active_row.side_effect = [
            (2, 'Test Item', 1.99, 'Description'),
            (1, 'Category')
        ]
        
        response = validate_entities_exist(self.mock_cursor, 1, 2)
        
        self.assertIsNone(response)
        self.assertEqual(mock_get_active_row.call_count, 2)
    
    @patch('api.item_categories.add_item_to_category.add_item_to_category.get_active_row_from_table')
    def test_validate_entities_throws_error_with_no_active_category(self, mock_get_active_row):
        mock_get_active_row.side_effect = [
            (2, 'Test Item', 1.99, 'Description'),
            ()
        ]
        
        response = validate_entities_exist(self.mock_cursor, 1, 2)
        expected_response = {'statusCode': 400, 'body': json.dumps({'error' : f'No Active Category found at ID: 1'})}
        
        self.assertEqual(response, expected_response)
        self.assertEqual(mock_get_active_row.call_count, 2)

    @patch('api.item_categories.add_item_to_category.add_item_to_category.get_active_row_from_table')
    def test_validate_entities_throws_error_with_no_active_item(self, mock_get_active_row):
        mock_get_active_row.side_effect = [
            (),
            (1, 'Category')
        ]
        
        response = validate_entities_exist(self.mock_cursor, 1, 2)
        expected_response = {'statusCode': 400, 'body': json.dumps({'error' : f'No Active Item found at ID: 2'})}
        
        self.assertEqual(response, expected_response)
        self.assertEqual(mock_get_active_row.call_count, 1)

    @patch('api.item_categories.add_item_to_category.add_item_to_category.get_active_row_from_table')
    def test_validate_entities_throws_error_when_no_active_entities(self, mock_get_active_row):
        mock_get_active_row.side_effect = [
            (),
            ()
        ]
        
        response = validate_entities_exist(self.mock_cursor, 1, 2)
        expected_response = {'statusCode': 400, 'body': json.dumps({'error' : f'No Active Item found at ID: 2'})}
        
        self.assertEqual(response, expected_response)
        self.assertEqual(mock_get_active_row.call_count, 1)

    def test_create_item_category_association_returns_none_for_success(self):
        self.mock_cursor.execute.return_value = (2, 1)

        response = create_item_category_association(self.mock_cursor, 1, 2)
        
        self.assertIsNone(response)
        self.assertEqual(self.mock_cursor.execute.call_count, 1)

    def test_create_item_category_association_throws_unique_validation_error(self):
        self.mock_cursor.execute.side_effect = psycopg2.errors.UniqueViolation

        response = create_item_category_association(self.mock_cursor, 1, 2)
        expected = {'statusCode': 400, 'body': json.dumps({'error' : f'Item at ID 2 is already added to Category with ID 1'})}
        
        self.assertEqual(response, expected)
        self.assertEqual(self.mock_cursor.execute.call_count, 1)

    @patch('api.item_categories.add_item_to_category.add_item_to_category.get_db_connection')
    @patch('api.item_categories.add_item_to_category.add_item_to_category.validate_entities_exist')
    @patch('api.item_categories.add_item_to_category.add_item_to_category.create_item_category_association')
    def test_post_item_to_category_in_db_returns_success_json(self, mock_create_association, mock_validate_entities, mock_get_db_connection):
        mock_get_db_connection.return_value.__enter__.return_value = self.mock_conn
        self.mock_conn.cursor.return_value.__enter__.return_value = self.mock_cursor

        mock_validate_entities.return_value = None
        mock_create_association.return_value = None

        response = post_item_to_category_in_db(1, 2)

        self.assertEqual(response['statusCode'], 201)
        self.assertEqual(json.loads(response['body']), {'message': 'Successfully added Item at ID 2 to Category at ID 1'})
        mock_validate_entities.assert_called_once_with(self.mock_cursor, 1, 2)
        mock_create_association.assert_called_once_with(self.mock_cursor, 1, 2)
        self.mock_conn.commit.assert_called_once()

    @patch('api.item_categories.add_item_to_category.add_item_to_category.get_db_connection')
    @patch('api.item_categories.add_item_to_category.add_item_to_category.validate_entities_exist')
    @patch('api.item_categories.add_item_to_category.add_item_to_category.create_item_category_association')
    def test_post_item_to_category_returns_validation_error(self, mock_create_association, mock_validate_entities, mock_get_db_connection):
        mock_get_db_connection.return_value.__enter__.return_value = self.mock_conn
        self.mock_conn.cursor.return_value.__enter__.return_value = self.mock_cursor

        mock_validate_entities.return_value = {'statusCode': 400, 'body': json.dumps({'error': 'Invalid or missing ID in path. Must use query string parameter labeled itemID'})}
        mock_create_association.return_value = None

        response = post_item_to_category_in_db(1, 2)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body']), {'error': 'Invalid or missing ID in path. Must use query string parameter labeled itemID'})
        mock_validate_entities.assert_called_once_with(self.mock_cursor, 1, 2)
        mock_create_association.assert_not_called()
        self.mock_conn.commit.assert_not_called()

    @patch('api.item_categories.add_item_to_category.add_item_to_category.get_db_connection')
    @patch('api.item_categories.add_item_to_category.add_item_to_category.validate_entities_exist')
    @patch('api.item_categories.add_item_to_category.add_item_to_category.create_item_category_association')
    def test_post_item_to_category_returns_association_error(self, mock_create_association, mock_validate_entities, mock_get_db_connection):
        mock_get_db_connection.return_value.__enter__.return_value = self.mock_conn
        self.mock_conn.cursor.return_value.__enter__.return_value = self.mock_cursor

        mock_validate_entities.return_value = None
        mock_create_association.return_value = {'statusCode': 400, 'body': json.dumps({'error' : 'Item at ID 2 is already added to Category with ID 1'})}

        response = post_item_to_category_in_db(1, 2)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body']), {'error': 'Item at ID 2 is already added to Category with ID 1'})
        mock_validate_entities.assert_called_once_with(self.mock_cursor, 1, 2)
        mock_create_association.assert_called_once_with(self.mock_cursor, 1, 2)
        self.mock_conn.commit.assert_not_called()
    
    @patch('api.item_categories.add_item_to_category.add_item_to_category.get_db_connection')
    def test_post_item_to_category_returns_psycopg2_error_json(self, mock_get_db_connection):
        mock_get_db_connection.return_value.__enter__.side_effect = psycopg2.Error

        response = post_item_to_category_in_db(1, 2)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body']), {'error': 'Database error'})
        self.mock_conn.commit.assert_not_called()

    @patch('api.item_categories.add_item_to_category.add_item_to_category.get_db_connection')
    def test_post_item_to_category_returns_exception_json(self, mock_get_db_connection):
        mock_get_db_connection.return_value.__enter__.side_effect = Exception

        response = post_item_to_category_in_db(1, 2)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body']), {'error': 'Internal server error'})
        self.mock_conn.commit.assert_not_called()
   
    @patch('api.item_categories.add_item_to_category.add_item_to_category.extract_and_validate_ids')
    def test_lambda_handler_returns_exception_json(self, mock_validate_ids):
        mock_validate_ids.side_effect = Exception

        response = lambda_handler({}, None)

        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(json.loads(response['body']), {'error': 'Internal server error'})

    @patch('api.item_categories.add_item_to_category.add_item_to_category.extract_and_validate_ids')
    def test_lambda_handler_returns_validation_error_json(self, mock_validate_ids):
        mock_validate_ids.return_value = {'statusCode': 400, 'body': json.dumps({'error': 'Invalid or missing ID in path. Must use query string parameter labeled itemID'})}

        response = lambda_handler({}, None)

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(json.loads(response['body']), {'error': 'Invalid or missing ID in path. Must use query string parameter labeled itemID'})

    @patch('api.item_categories.add_item_to_category.add_item_to_category.extract_and_validate_ids')
    @patch('api.item_categories.add_item_to_category.add_item_to_category.post_item_to_category_in_db')
    def test_lambda_handler_success(self, mock_post_item_to_category, mock_validate_ids):
        mock_validate_ids.return_value = (1, 2)
        mock_post_item_to_category.return_value = {'statusCode': 201, 'body': json.dumps({'message': 'Successfully added Item at ID 2 to Category at ID 1'})}

        response = lambda_handler({}, None)

        self.assertEqual(response['statusCode'], 201)
        self.assertEqual(json.loads(response['body']), {'message': 'Successfully added Item at ID 2 to Category at ID 1'})
