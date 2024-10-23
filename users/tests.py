from django.test import TestCase

from users.services import UserService


class UserTest(TestCase):
    def test_user_register(self):
        email = 'rtest@mail.com'
        password = 'rtest'

        user, error = UserService.register_user(None, None)
        self.assertIsNotNone(error)

        user, error = UserService.register_user(email, None)
        self.assertIsNotNone(error)

        user, error = UserService.register_user('', password)
        self.assertIsNotNone(error)

        user, error = UserService.register_user(email, password)
        self.assertIsNotNone(user)
        self.assertIsNone(error)

        user, error = UserService.register_user(email, password)
        self.assertIsNone(user)
        self.assertIsNotNone(error)
