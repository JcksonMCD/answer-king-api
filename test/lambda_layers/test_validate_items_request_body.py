import json
import unittest
from api.lambda_layers.utils.python.utils.validation import validate_item_event_body
from api.lambda_layers.utils.python.utils.custom_exceptions import ValidationError
from api.lambda_layers.utils.python.utils.models import Item

class TestValidateItemsRequestBody(unittest.TestCase):

    def test_validate_event_body_returns_tuple(self):
        event = {'body': json.dumps({'name': 'Created', 'price': 1.99, 'description': 'Created description'})}

        response = validate_item_event_body(event)
        expected_item = Item(name='Created', price=1.99, description='Created description')

        self.assertEqual(response, expected_item)
        self.assertEqual(response.price, 1.99)
        self.assertEqual(response.description, 'Created description')

    def test_validate_event_body_returns_tuple_with_empty_description(self):
        event = {'body': json.dumps({'name': 'Created', 'price': 1.99})}
        response = validate_item_event_body(event)
        expected_item = Item(name='Created', price=1.99, description=None)

        self.assertEqual(response, expected_item)
        self.assertEqual(response.price, 1.99)
        self.assertEqual(response.description, None)

    def test_validate_event_body_throws_error_with_empty_name(self):
        event = {'body': json.dumps({'name': ' ', 'price': 1.99, 'description': 'Some description'})}
        with self.assertRaises(ValidationError) as context:
            validate_item_event_body(event)
        self.assertIn('Name field must not be empty', str(context.exception))

    def test_validate_event_body_throws_error_with_missing_name(self):
        event = {'body': json.dumps({'price': 1.99, 'description': 'Some description'})}
        with self.assertRaises(ValidationError) as context:
            validate_item_event_body(event)
        self.assertIn('Field required', str(context.exception))

    def test_validate_event_body_throws_error_with_non_string_name(self):
        event = {'body': json.dumps({'name': 123, 'price': 1.99, 'description': 'Some description'})}
        with self.assertRaises(ValidationError) as context:
            validate_item_event_body(event)
        self.assertIn('Value error, Name must be of type string', str(context.exception))

    def test_validate_event_body_throws_error_with_negative_price(self):
        event = {'body': json.dumps({'name': 'Created', 'price': -1.99, 'description': 'Some description'})}
        with self.assertRaises(ValidationError) as context:
            validate_item_event_body(event)
        self.assertIn('Price cannot be negative', str(context.exception))

    def test_validate_event_body_throws_error_with_missing_price(self):
        event = {'body': json.dumps({'name': 'Created', 'description': 'Some description'})}
        with self.assertRaises(ValidationError) as context:
            validate_item_event_body(event)
        self.assertIn('Field required', str(context.exception))

    def test_validate_event_body_throws_error_with_price_not_two_decimal_places(self):
        event = {'body': json.dumps({'name': 'Created', 'price': 1.999, 'description': 'Some description'})}
        with self.assertRaises(ValidationError) as context:
            validate_item_event_body(event)
        self.assertIn('Price has to be to two decimal points', str(context.exception))

    def test_validate_event_body_throws_error_with_invalid_price_format(self):
        event = {'body': json.dumps({'name': 'Created', 'price': 'free', 'description': 'Some description'})}
        with self.assertRaises(ValidationError) as context:
            validate_item_event_body(event)
        self.assertIn('Value error, Price must be a number', str(context.exception))

    def test_validate_event_body_throws_error_with_invalid_json(self):
        event = {'body': 'name: Created, price: 1.99, description: some description'}
        with self.assertRaises(ValidationError) as context:
            validate_item_event_body(event)
        self.assertIn('Invalid JSON format', str(context.exception))

    def test_validate_event_body_throws_error_with_missing_body(self):
        event = {}
        with self.assertRaises(ValidationError) as context:
            validate_item_event_body(event)
        self.assertIn('Request body is required', str(context.exception))
