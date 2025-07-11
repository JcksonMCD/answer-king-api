import unittest
from api.lambda_layers.utils.python.utils.validation import extract_id_path_param
from api.lambda_layers.utils.python.utils.custom_exceptions import ValidationError


class TestExtractIdPathParam(unittest.TestCase):

    def test_extract_item_id_returns_id(self):
        event = {'pathParameters': {'id': '1'}}
        result = extract_id_path_param(event)
        self.assertEqual(result, 1)

    def test_raises_error_with_blank_id(self):
        event = {'pathParameters': {'id': ''}}
        with self.assertRaises(ValidationError) as context:
            extract_id_path_param(event)
        self.assertIn('Invalid or missing path ID', str(context.exception))

    def test_raises_error_with_non_integer_id(self):
        event = {'pathParameters': {'id': 'abc'}}
        with self.assertRaises(ValidationError) as context:
            extract_id_path_param(event)
        self.assertIn('ID must be an integer', str(context.exception))

    def test_raises_error_with_missing_path_param(self):
        event = {}
        with self.assertRaises(ValidationError) as context:
            extract_id_path_param(event)
        self.assertIn('Invalid or missing path ID', str(context.exception))

