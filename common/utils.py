import os
from datetime import datetime, timedelta, timezone

from jwt import JWT, jwk_from_dict
from jwt.utils import get_int_from_datetime
from rest_framework import status
from rest_framework.response import Response


def bad(error):
    """
    Returns a Response object with error
    To minimize the effort in views
    """
    return Response(
        {
            'error': error
        },
        status=status.HTTP_400_BAD_REQUEST
    )


def ok(data=None, message=None):
    """
        Returns a Response object with data
        To minimize the effort in views
        """
    if message:
        return Response(
            {
                'message': message
            },
            status=status.HTTP_200_OK
        )
    return Response(
        {
            'data': data
        },
        status=status.HTTP_200_OK
    )


jwt_util = JWT()

def get_jwt_token(claims):
    """
    Creates a JWT token
    :param claims: dict of claims like email, role etc.
    :returns token: jwt token
    """
    claims['iat'] = get_int_from_datetime(datetime.now(timezone.utc))
    claims['exp'] = get_int_from_datetime(
        datetime.now(timezone.utc) + timedelta(hours=60)
    )

    token = jwt_util.encode(claims, os.getenv('JWT_KEY'))
    return token


def decode_jwt_token(token):
    """
    Decodes a jwt token

    :param token: jwt token in str
    :returns claims: dict of claims email, role etc
    """
    try:
        claims = jwt_util.decode(token, JWT_SIGNING_KEY, do_time_check=True)
        return claims
    except Exception:
        return None
