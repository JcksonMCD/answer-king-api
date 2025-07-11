import unittest
from unittest.mock import Mock
from api.lambda_layers.utils.python.utils.validation import get_active_row_from_table
from api.lambda_layers.utils.python.utils.custom_exceptions import ValidationError, ActiveResourceNotFoundError


class TestGetActiveRowFromTable(unittest.TestCase):
    def setUp(self):
        self.mock_cursor = Mock()
        self.valid_id = 1

    def test_returns_active_row_for_valid_table_names(self):
        valid_table_names = ['categories', 'items', 'orders', 'item_categories']

        for table_name in valid_table_names:
            self.mock_cursor.fetchone.return_value = (1,)
            result = get_active_row_from_table(self.mock_cursor, table_name, self.valid_id)
            self.assertEqual(result, (1,))

        self.assertEqual(self.mock_cursor.execute.call_count, 4)
        self.assertEqual(self.mock_cursor.fetchone.call_count, 4)

    def test_raises_error_if_no_active_row_found(self):
        self.mock_cursor.fetchone.return_value = None

        with self.assertRaises(ActiveResourceNotFoundError):
            get_active_row_from_table(self.mock_cursor, "items", self.valid_id)

        self.mock_cursor.execute.assert_called_once()
        self.mock_cursor.fetchone.assert_called_once()

    def test_handles_capitalized_table_names(self):
        valid_table_names = ['Categories', 'iTems', 'orDers', 'item_Categories']
        self.mock_cursor.fetchone.return_value = (1,)

        for table_name in valid_table_names:
            result = get_active_row_from_table(self.mock_cursor, table_name, self.valid_id)
            self.assertEqual(result, (1,))

        self.assertEqual(self.mock_cursor.execute.call_count, 4)
        self.assertEqual(self.mock_cursor.fetchone.call_count, 4)

    def test_raises_validation_error_for_empty_table_name(self):
        with self.assertRaises(ValidationError):
            get_active_row_from_table(self.mock_cursor, '', self.valid_id)

        self.mock_cursor.execute.assert_not_called()
        self.mock_cursor.fetchone.assert_not_called()

    def test_raises_validation_error_for_invalid_table_name(self):
        invalid_table_name = 'nonexistent_table'

        with self.assertRaises(ValidationError) as context:
            get_active_row_from_table(self.mock_cursor, invalid_table_name, self.valid_id)

        self.assertIn(f"Invalid table name: {invalid_table_name}", str(context.exception))
        self.mock_cursor.execute.assert_not_called()
        self.mock_cursor.fetchone.assert_not_called()
