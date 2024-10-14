from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from common import utils
from common.decorators import authenticated
from drone.models import Drone
from users.models import User


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@authenticated()
def drone_view(request, **kwargs):
    email = kwargs['email']
    user = User.objects.get(email=email)
    if request.method == 'GET':
        drones = Drone.objects.filter(user=user)
        drone_data = [
            drone.to_dict()
            for drone in drones
        ]
        return utils.ok(drone_data)

    elif request.method == 'POST':
        name = request.data.get('name', 'raju')
        avg_speed_ms = request.data.get('avg_speed_ms', None)
        flight_time_seconds = request.data.get('flight_time_seconds', None)

        if not flight_time_seconds:
            return utils.bad('flight time is required!')

        drone = Drone(
            name=name,
            avg_speed_ms=avg_speed_ms,
            flight_time_seconds=flight_time_seconds,
            user=user
        )
        drone.save()
        return utils.ok(drone.to_dict())
    elif request.method == 'PUT':
        drone_id = request.data.get('id')
        if not drone_id:
            return utils.bad('please provide drone id')
        drone = Drone.objects.get(id=drone_id, user=user)

        if not drone:
            return utils.bad(f'drone with id {drone_id} not found')
        try:
            drone.name = request.data.get('name', drone.name)
            drone.avg_speed_ms = request.data.get('avg_speed_ms', drone.avg_speed_ms)
            drone.flight_time_seconds = request.data.get('flight_time_seconds', drone.flight_time_seconds)
            drone.save()
            return utils.ok(drone.to_dict())
        except Exception:
            return Response(
                {
                    'error': f'failed to update drone with id {drone_id}'
                },
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    elif request.method == 'DELETE':
        drone_id = request.data.get('id')
        if not drone_id:
            return utils.bad('drone id is required')
        drone = Drone.objects.get(id=drone_id, user=user)
        if not drone:
            return utils.bad(f'drone with id {drone_id} not found!')

        drone.delete()
        return utils.ok(message=f'drone with id {drone_id} deleted!')