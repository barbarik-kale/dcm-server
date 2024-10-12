from django.test import TestCase
from rest_framework import status

from common import utils
from common.utils import get_jwt_token, decode_jwt_token


class UtilsTest(TestCase):
    def test_ok(self):
        data = {
            'age': 18
        }
        response = utils.ok(data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK, 'status must be 200')
        self.assertEqual(response.data, {'data':data}, 'data must be same')

        message = 'this is simple test message'
        response = utils.ok(message=message)

        self.assertEqual(response.status_code, status.HTTP_200_OK, 'status must be 200')
        self.assertEqual(response.data, {'message': message}, 'data must be same')


    def test_bad(self):
        error = 'this is simple error message'
        response = utils.bad(error)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 'status must be 400')
        self.assertEqual(response.data, {'error': error}, 'data must be same')


class JWTTest(TestCase):
    def test_jwt(self):
        claims = {
            'email': 'test@mail.com',
            'role': 'admin'
        }
        token = get_jwt_token(claims)

        self.assertIsNotNone(token)

        claims_2 = decode_jwt_token(token)

        self.assertEqual(claims['email'], claims_2.get('email', None))
        self.assertEqual(claims['role'], claims_2.get('role', None))
