from common.utils import get_jwt_token
from users.models import User


class UserService:
    @staticmethod
    def get_user(email):
        try:
            user = User.objects.get(email=email)
            return user.to_dict()
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_all_users():
        try:
            users = User.objects.all()
            users = [
                user.to_dict()
                for user in users
            ]
            return users
        except Exception as e:
            return []

    @staticmethod
    def register_user(email, password):
        if email and password:
            user = UserService.get_user(email)
            if user:
                return None, 'email is already registered!'

            try:
                user = User(email=email, password=password)
                user.save()
                return user, 'email registered'
            except Exception as e:
                return None, str(e)
        else:
            return None, 'please provide email and password'

    @staticmethod
    def login_user(email, password):
        if email and password:
            try:
                user = User.objects.get(email=email)
                if not user:
                    return None, f'account with email {email} does not exist'

                if user.password == password:
                    return get_jwt_token({
                        'email': email
                    }), 'login success'
                else:
                    return None, 'invalid email or password'
            except User.DoesNotExist:
                return None, 'invalid email or password'
        else:
            return None, 'please provide email and password'

