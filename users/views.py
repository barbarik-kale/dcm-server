from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from common import utils
from common.decorators import authenticated
from users.services import UserService


@api_view(['POST'])
def user_register(request):
    """
    Register a user account
    """
    email = request.data.get('email')
    password = request.data.get('password')

    try:
        user, error = UserService.register_user(email, password)
        if error:
            return utils.bad(error)
        return utils.ok(user)
    except Exception:
        return Response({'message': 'something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def user_login(request):
    """
    Validate email and password and return JWT token
    """
    email = request.data.get('email')
    password = request.data.get('password')

    try:
        token, error = UserService.login_user(email, password)
        if error:
            return utils.bad(error)
        return utils.ok({
            'token': token
        })
    except Exception:
        return Response({'message': 'something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@authenticated()
def user_list(request, **kwargs):
    try:
        users = UserService.get_all_users()
        return utils.ok(users)
    except Exception:
        return Response({'message': 'something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

