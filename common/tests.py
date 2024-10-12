from django.test import TestCase
from rest_framework import status

from common import utils


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