import json
import unittest
import logging
from api.lambda_layers.validate_item_id_query_param.python.validate_item_id_query_param import extract_item_id

class TestValidateItemIdQueryParam(unittest.TestCase):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    def test_extract_id_returns_id(self):
        event = {'queryStringParameters': {'itemID': 1}}

        response = extract_item_id(event, self.logger)

        self.assertEqual(response, 1)

    def test_extract_id_throws_error_with_incorrect_path(self):
        event = {'queryStringParameters': {'id': 1}}

        response = extract_item_id(event, self.logger)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Invalid or missing ID in path. Must use query string parameter labeled itemID")

    def test_extract_id_throws_error_with_non_numerical_path(self):
        event = {'queryStringParameters': {'itemID': 'itemID'}}

        response = extract_item_id(event, self.logger)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "ID must be an integer")

    def test_extract_id_throws_error_with_null_id(self):
        event = {'queryStringParameters': {'itemID': None}}
        response = extract_item_id(event, self.logger)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Invalid or missing ID in path. Must use query string parameter labeled itemID")

    def test_extract_id_throws_error_with_missing_path(self):
        response = extract_item_id({}, self.logger)
        body = json.loads(response['body'])

        self.assertEqual(response['statusCode'], 400)
        self.assertEqual(body["error"], "Invalid or missing ID in path. Must use query string parameter labeled itemID")