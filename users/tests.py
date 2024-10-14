from django.test import TestCase

from users.services import UserService


class UserTest(TestCase):
    def test_user_service(self):
        email = 'test@mail.com'
        password = 'test'

        token, error = UserService.login_user(email, password)
        self.assertIsNone(token)

        user = UserService.get_user(email)
        self.assertIsNone(user)

        user, error = UserService.register_user(email, password)
        self.assertIsNotNone(user)
        self.assertEqual(email, user.email)

        token, error = UserService.login_user(email, password)
        self.assertIsNotNone(token)

        user, error = UserService.register_user(email, password)
        self.assertIsNone(user)
