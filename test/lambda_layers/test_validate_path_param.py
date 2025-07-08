import json
import unittest
import logging
from api.lambda_layers.validate_id_path_param.python.validate_id_path_param import extract_id

class TestValidateIdPathParam(unittest.TestCase):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    def test_extract_id_returns_id(self):
        event = {'pathParameters' : {'id' : 1}}

        response = extract_id(event, self.logger)

        self.assertEqual(response, 1)

    def test_extract_id_throws_error_with_incorrect_path(self):
        event = {'pathParameters' : {'id' : ''}}

        response = extract_id(event, self.logger)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Invalid or missing ID in path")

    def test_extract_id_throws_error_with_non_numerical_path(self):
        event = {'pathParameters' : {'id' : 'id'}}

        response = extract_id(event, self.logger)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "ID must be an integer")

    def test_extract_id_throws_error_with_missing_path(self):
        response = extract_id({}, self.logger)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Invalid or missing ID in path")