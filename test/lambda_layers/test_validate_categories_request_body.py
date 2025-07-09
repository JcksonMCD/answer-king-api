import json
import unittest
import logging
from api.lambda_layers.validate_categories_request_body.python.validate_categories_request_body import validate_event_body

class TestValidateItemsRequestBody(unittest.TestCase):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    def test_validate_event_body_returns_category_name(self):
        event = {'body' : json.dumps({'name' : 'Category Name'})}

        response = validate_event_body(event, self.logger)

        self.assertEqual(response, ('Category Name'))

    def test_validate_event_body_throws_error_with_empty_name(self):
        event = {'body' : json.dumps({'name' : ' '})}

        response = validate_event_body(event, self.logger)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Name field must not be empty")

    def test_validate_event_body_throws_error_with_name_missing(self):
        event = {'body' : json.dumps({})}

        response = validate_event_body(event, self.logger)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Name field is required and must be of type string")

    def test_validate_event_body_throws_error_with_non_string_name(self):
        event = {'body' : json.dumps({'name': 1})}

        response = validate_event_body(event, self.logger)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Name field is required and must be of type string")

    def test_validate_event_body_throws_error_with_body_as_string(self):
        event = {'body' : 'name : Category name'}

        response = validate_event_body(event, self.logger)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Invalid JSON format")

    def test_validate_event_body_throws_error_with_missing_body(self):
        response = validate_event_body({}, self.logger)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Request body is required")