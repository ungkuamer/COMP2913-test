import unittest
from flask import url_for
from server import app

class TestFlaskApp(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_home_page(self):
        response = self.app.get('/')

    def test_register_page(self):
        response = self.app.get('/user/register')
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        response = self.app.get('/user/login')
        self.assertEqual(response.status_code, 200)

    # Test if logout page redirects to login page
    def test_logout(self):
        response = self.app.get('/logout', follow_redirects=True)
        self.assertIn(b'Login', response.data)

    # Add more test cases for other routes as needed...

if __name__ == '__main__':
    unittest.main()