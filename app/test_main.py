'''
Unit tests for the main API
'''
# Standard imports
import os
import sys
import unittest

# Third-party imports
from fastapi.testclient import TestClient

# Add the root project directory to the path
ROOT_PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_PROJECT_DIR)

# Local imports
from app.main import app    # pylint: disable = wrong-import-position

client = TestClient(app)

class TestMain(unittest.TestCase):
    '''
    A set of unit tests for the main API
    '''

    def test_read_root_get(self):
        '''
        Tests the root path responds to GET requests
        '''
        response = client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_read_root_welcome_message(self):
        '''
        Tests the root path responds with a welcome message
        '''
        response = client.get("/")
        self.assertEqual(response.json(), {"message": "Welcome!"})

if __name__ == '__main__':
    unittest.main()
