from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from common import utils
from common.decorators import authenticated
from drone.services import DroneService
from ws.services import TokenService


@api_view(['POST'])
@authenticated()
def get_ws_token(request, **kwargs):
    try:
        drone_id = request.data.get('drone_id')
        email = kwargs['email']
        token, error = TokenService.get_ws_token(drone_id, email)
        if error:
            return utils.bad(error)
        return utils.ok(data={'token': token})
    except Exception:
        return Response({'message': 'something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
