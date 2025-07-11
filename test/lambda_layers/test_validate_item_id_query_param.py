import unittest
from api.lambda_layers.utils.python.utils.validation import extract_item_id_from_query_param
from api.lambda_layers.utils.python.utils.custom_exceptions import ValidationError

class TestExtractItemIdFromQueryParam(unittest.TestCase):

    def test_extract_id_returns_integer_id(self):
        event = {'queryStringParameters': {'itemID': '1'}}
        result = extract_item_id_from_query_param(event)
        self.assertEqual(result, 1)

    def test_raises_error_with_missing_itemID_key(self):
        event = {'queryStringParameters': {'id': '1'}}
        with self.assertRaises(ValidationError) as context:
            extract_item_id_from_query_param(event)
        self.assertIn('Invalid or missing ID in path', str(context.exception))

    def test_raises_error_with_non_integer_value(self):
        event = {'queryStringParameters': {'itemID': 'itemID'}}
        with self.assertRaises(ValidationError) as context:
            extract_item_id_from_query_param(event)
        self.assertIn('ID must be an integer', str(context.exception))

    def test_raises_error_with_null_itemID(self):
        event = {'queryStringParameters': {'itemID': None}}
        with self.assertRaises(ValidationError) as context:
            extract_item_id_from_query_param(event)
        self.assertIn('Invalid or missing ID in path', str(context.exception))

    def test_raises_error_with_missing_query_parameters(self):
        event = {}
        with self.assertRaises(ValidationError) as context:
            extract_item_id_from_query_param(event)
        self.assertIn('Invalid or missing ID in path', str(context.exception))
