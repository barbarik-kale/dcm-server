from django.test import TestCase

from common.utils import decode_jwt_token
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

    def test_user_login(self):
        email = 'test@mail.com'
        password = 'test'

        token, error = UserService.login_user(email, None)
        self.assertIsNotNone(error)

        token, error = UserService.login_user(email, password)
        self.assertIsNotNone(error)

        user, error = UserService.register_user(email, password)
        self.assertIsNotNone(user)

        user, error = UserService.login_user(email, password + password)
        self.assertIsNotNone(error)

        token, error = UserService.login_user(email, password)
        self.assertIsNone(error)
        self.assertIsNotNone(token)

        claims = decode_jwt_token(token)
        self.assertIsNotNone(claims)
        self.assertEqual(email, claims.get('email', None))

    def test_user_list(self):
        users = UserService.get_all_users()
        self.assertEqual(len(users), 0)

        user, error = UserService.register_user('test1@mail.com', 'test1')
        user, error = UserService.register_user('test2@mail.com', 'test2')
        user, error = UserService.register_user('test3@mail.com', 'test3')
        users = UserService.get_all_users()
        self.assertEqual(len(users), 3)

    def test_get_user(self):
        email, password = 'test@mail.com', 'test'

        user, error = UserService.register_user(email, password)
        self.assertIsNotNone(user)

        user = UserService.get_user(email)
        self.assertEqual(email, user.email)
        self.assertEqual(password, user.password)

