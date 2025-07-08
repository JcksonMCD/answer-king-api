import json
import unittest
import logging
from api.lambda_layers.validate_items_request_body.python.validate_items_request_body import validate_event_body

class TestValidateItemsRequestBody(unittest.TestCase):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    def test_validate_event_body_returns_tuple(self):
        event = {'body' : json.dumps({'name' : 'Created', 'price' : 1.99, 'description': 'Created description'})}

        response = validate_event_body(event, self.logger)

        self.assertEqual(response, ('Created', 1.99, 'Created description'))

    def test_validate_event_body_returns_tuple_with_empty_description(self):
        event = {'body' : json.dumps({'name' : 'Created', 'price' : 1.99})}

        response = validate_event_body(event, self.logger)

        self.assertEqual(response, ('Created', 1.99, None))

    def test_validate_event_body_throws_error_with_empty_name(self):
        event = {'body' : json.dumps({'name': ' ', 'price' : 1.99, 'description': 'Created iteam'})}

        response = validate_event_body(event, self.logger)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Name field must not be empty")

    def test_validate_event_body_throws_error_with_name_missing(self):
        event = {'body' : json.dumps({'price' : 1.99, 'description': 'Created iteam'})}

        response = validate_event_body(event, self.logger)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Name field is required and must be of type string")

    def test_validate_event_body_throws_error_with_non_string_name(self):
        event = {'body' : json.dumps({'name': 1, 'price' : 1.99, 'description': 'Created iteam'})}

        response = validate_event_body(event, self.logger)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Name field is required and must be of type string")

    def test_validate_event_body_throws_error_with_negative_price(self):
        event = {'body' : json.dumps({'name' : 'Created', 'price': -1.99, 'description': 'Created iteam'})}

        response = validate_event_body(event, self.logger)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Price cannot be negative")

    def test_validate_event_body_throws_error_with_price_missing(self):
        event = {'body' : json.dumps({'name' : 'Created', 'description': 'Created iteam'})}

        response = validate_event_body(event, self.logger)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Price is required")

    def test_validate_event_body_throws_error_with_price_is_not_to_two_dp(self):
        event = {'body' : json.dumps({'name' : 'Created', 'price': 1.999, 'description': 'Created iteam'})}

        response = validate_event_body(event, self.logger)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Price has to be to two decimal points")

    def test_validate_event_body_throws_error_with_string_price(self):
        event = {'body' : json.dumps({'name' : 'Created', 'price' : 'One Pound', 'description': 'Created iteam'})}

        response = validate_event_body(event, self.logger)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Price must be a valid number")

    def test_validate_event_body_throws_error_with_body_as_string(self):
        event = {'body' : 'id: 1, name : Created, price : 1.99, description: Created iteam'}

        response = validate_event_body(event, self.logger)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Invalid JSON format")

    def test_validate_event_body_throws_error_with_missing_body(self):
        response = validate_event_body({}, self.logger)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Request body is required")