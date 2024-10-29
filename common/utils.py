import os
from datetime import datetime, timedelta, timezone

import jwt
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


def get_jwt_token(claims):
    """
    This method performs an unsafe operation.
    WARNING: This JWT generate approach is not recommended.
    Please use appropriate rsa in production

    Creates a JWT token
    :param claims: dict of claims like email, role etc.
    :returns token: jwt token
    """
    claims['iat'] = datetime.now(timezone.utc)
    claims['exp'] = datetime.now(timezone.utc) + timedelta(hours=60)

    token = jwt.encode(claims, os.getenv('JWT_SECRET'), algorithm='HS256')
    return token


def decode_jwt_token(token):
    """
    This method performs an unsafe operation.
    WARNING: This JWT decode approach is not recommended.
    Please use appropriate rsa in production

    Decodes a jwt token

    :param token: jwt token in str
    :returns claims: dict of claims email, role etc
    """
    try:
        return jwt.decode(token, os.getenv('JWT_SECRET'), algorithms='HS256')
    except Exception:
        return None
