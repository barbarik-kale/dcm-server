from rest_framework import status
from rest_framework.response import Response

from api.utils import decode_jwt_token

"""
Apply on views which needs authentication
@authenticated views needs to take **kwargs as the last parameter
"""
def authenticated():
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            token = request.META.get('HTTP_AUTHORIZATION')
            if token:
                claims = decode_jwt_token(token)
                if not claims:
                    return Response(
                        status=status.HTTP_401_UNAUTHORIZED
                    )

                for key in claims:
                    kwargs[key] = claims[key]
                return view_func(request, *args, **kwargs)

            return Response(
                status=status.HTTP_401_UNAUTHORIZED
            )
        return _wrapped_view
    return decorator