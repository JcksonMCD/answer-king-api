import unittest
from unittest.mock import Mock
import pytest
from api.lambda_layers.get_active_row_from_table.python.get_active_row_from_table import get_active_row_from_table 

class TestGetActiveRowFromTable(unittest.TestCase):
    def setUp(self):
        self.mock_cursor = Mock()
        self.valid_id = 1

    def test_get_active_row_from_table_returns_active_row_for_valid_table_names(self):
        valid_table_names = ['categories', 'items', 'orders', 'item_categories']
        self.mock_cursor.fetchone.return_value = (1,)

        for table_name in valid_table_names:
            result = get_active_row_from_table(self.mock_cursor, table_name, 1)

            self.assertEqual(result, (1,))
        
        self.mock_cursor.execute.call_count == 4
        self.mock_cursor.fetchone.call_count == 4

    def test_get_active_row_from_table_returns_empty_tuple_if_no_row(self):
        self.mock_cursor.fetchone.return_value = ()

        result = get_active_row_from_table(self.mock_cursor, "items", 1)

        self.assertEqual(result, ())
        self.mock_cursor.execute.assert_called_once()
        self.mock_cursor.fetchone.assert_called_once()

    def test_get_active_row_from_table_handles_caps_in_table_name(self):
        valid_table_names = ['Categories', 'iTems', 'orDers', 'item_Categories']
        self.mock_cursor.fetchone.return_value = (1,)

        for table_name in valid_table_names:
            result = get_active_row_from_table(self.mock_cursor, table_name, 1)

            self.assertEqual(result, (1,))
        
        self.mock_cursor.execute.call_count == 4
        self.mock_cursor.fetchone.call_count == 4

    def test_get_active_row_from_table_throws_error_with_no_table_name(self):
        with pytest.raises(ValueError, match=f"Invalid table name: "):
            get_active_row_from_table(self.mock_cursor, '', self.valid_id)
            
        self.mock_cursor.execute.assert_not_called()
        self.mock_cursor.fetchone.assert_not_called()

    def test_get_active_row_from_table_returns_error_for_unexcepted_table_name(self):
        invalid_table_name = "invalid_table_name"

        with pytest.raises(ValueError, match=f"Invalid table name: {invalid_table_name}"):
            get_active_row_from_table(self.mock_cursor, invalid_table_name, self.valid_id)
            
        self.mock_cursor.execute.assert_not_called()
        self.mock_cursor.fetchone.assert_not_called()
