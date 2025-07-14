import json
import unittest
from api.lambda_layers.utils.python.utils.validation import validate_category_event_body
from api.lambda_layers.utils.python.utils.custom_exceptions import ValidationError
from api.lambda_layers.utils.python.utils.models import Category

class TestValidateCategoryEventBody(unittest.TestCase):

    def test_validate_event_body_returns_category_name(self):
        event = {'body': json.dumps({'name': 'Category Name'})}
        response = validate_category_event_body(event)
        self.assertEqual(response, Category(name='Category Name'))

    def test_validate_event_body_throws_error_with_empty_name(self):
        event = {'body': json.dumps({'name': ' '})}
        with self.assertRaises(ValidationError) as context:
            validate_category_event_body(event)
        self.assertIn("Value error, Name field must not be empty", str(context.exception))

    def test_validate_event_body_throws_error_with_name_missing(self):
        event = {'body': json.dumps({})}
        with self.assertRaises(ValidationError) as context:
            validate_category_event_body(event)
        self.assertIn("Field required", str(context.exception))

    def test_validate_event_body_throws_error_with_non_string_name(self):
        event = {'body': json.dumps({'name': 1})}
        with self.assertRaises(ValidationError) as context:
            validate_category_event_body(event)
        self.assertIn("Value error, Name must be of type string", str(context.exception))

    def test_validate_event_body_throws_error_with_body_as_string(self):
        event = {'body': 'name : Category name'}
        with self.assertRaises(ValidationError) as context:
            validate_category_event_body(event)
        self.assertIn("Invalid JSON format", str(context.exception))

    def test_validate_event_body_throws_error_with_missing_body(self):
        event = {}
        with self.assertRaises(ValidationError) as context:
            validate_category_event_body(event)
        self.assertIn("Request body is required", str(context.exception))
