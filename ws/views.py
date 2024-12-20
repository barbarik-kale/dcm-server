from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from common import utils
from common.decorators import authenticated
from drone.services import DroneService


@api_view(['POST'])
@authenticated()
def get_ws_token(request, **kwargs):
    try:
        drone_id = request.data.get('drone_id')
        email = kwargs['email']
        if not drone_id:
            return utils.bad('drone_id is required!')

        drone, error = DroneService.get_drone(email, drone_id)
        if error:
            return utils.bad(error)

        claims = {
            'email': email,
            'drone_id': drone_id
        }
        token = utils.get_jwt_token(claims, True)
        return utils.ok(data={'token': token})
    except Exception:
        return Response({'message': 'something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
