from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from common import utils
from common.decorators import authenticated
from drone.services import DroneService
from users.services import UserService


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@authenticated()
def drone_view(request, **kwargs):
    email = kwargs['email']

    if request.method == 'GET':
        drone_id = request.data.get('drone_id', None)
        drone, error = DroneService.get_drone(email, drone_id)
        if error:
            return utils.bad(error)
        return utils.ok(drone.to_dict())

    elif request.method == 'POST':
        # Create a new drone
        name = request.data.get('name', 'raju')
        avg_speed_ms = request.data.get('avg_speed_ms')
        flight_time_seconds = request.data.get('flight_time_seconds')

        try:
            drone, error = DroneService.create_drone(email, name, avg_speed_ms, flight_time_seconds)
            if error:
                return utils.bad(error)
            return utils.ok(drone.to_dict())
        except Exception as e:
            return Response({'message': 'something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif request.method == 'PUT':
        # Update an existing drone
        drone_id = request.data.get('id')
        if not drone_id:
            return utils.bad('please provide drone id')

        details = {
            'name': request.data.get('name'),
            'avg_speed_ms': request.data.get('avg_speed_ms'),
            'flight_time_seconds': request.data.get('flight_time_seconds')
        }

        drone, message = DroneService.update_drone(email, drone_id, details)
        if drone is None:
            return utils.bad(message)
        return utils.ok(drone)

    elif request.method == 'DELETE':
        # Delete a drone
        drone_id = request.data.get('id')
        if not drone_id:
            return utils.bad('please provide drone id')

        success, message = DroneService.delete_drone(email, drone_id)
        if not success:
            return utils.bad(message)
        return utils.ok(message)


@api_view(['GET'])
@authenticated()
def get_drone_list(request, **kwargs):
    try:
        email = kwargs['email']
        drones, message = DroneService.get_drone_list(email)
        if message:
            return utils.bad(message)
        drones = [
            drone.to_dict()
            for drone in drones
        ]
        return utils.ok(drones)
    except Exception as e:
        return Response({'message': 'something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
