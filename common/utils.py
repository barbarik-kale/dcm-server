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


