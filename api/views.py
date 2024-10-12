from django.db import IntegrityError

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from api.decorators import authenticated
from api.models import User, Drone
from api.utils import get_jwt_token


@api_view(['POST'])
def user_register(request):
    """
    Register a user account
    """
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response(
            data={
                'message':'Please enter email and password'
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User(email=email, password=password)
        user.save()
        return Response(
            data={
                'message':f'Email {email} registered!'
            },
            status=status.HTTP_200_OK
        )
    except IntegrityError:
        return Response(
            data={
                'message': f'Email {email} is already registered!'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception:
        return Response(
            data={
                'message': f'Something went wrong'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def user_login(request):
    """
    Validate email and password and return JWT token
    """
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response(
            data={
                'message': 'please provide email and password'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        user = User.objects.get(email=email)
        if user.password == password:
            return Response(
                data={
                    'Authorization': get_jwt_token({'email': email})
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                data={
                    'message': 'invalid email or password!'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    except User.DoesNotExist:
        return Response(
            data={
                'message': 'invalid email or password'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        print(str(e))
        return Response(
            data={
                'message': 'Something went wrong!'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@authenticated()
def user_list(request, **kwargs):
    users = User.objects.all()
    users_data = [
        {
            'id': user.id,
            'email': user.email
        }
        for user in users
    ]
    return Response(
        data=users_data,
        status=status.HTTP_200_OK
    )

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
        return Response(
            {
                'data': drone_data
            },
            status=status.HTTP_200_OK
        )

    elif request.method == 'POST':
        name = request.data.get('name', 'raju')
        avg_speed_ms = request.data.get('avg_speed_ms', None)
        flight_time_seconds = request.data.get('flight_time_seconds', None)

        if not flight_time_seconds:
            return Response(
                {
                    'error': 'flight time is required'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        drone = Drone(
            name=name,
            avg_speed_ms=avg_speed_ms,
            flight_time_seconds=flight_time_seconds,
            user=user
        )
        drone.save()
        return Response(
            {
                'data': drone.to_dict()
            },
            status=status.HTTP_200_OK
        )
    elif request.method == 'PUT':
        drone_id = request.data.get('id')
        drone = Drone.objects.get(id=drone_id, user=user)

        if not drone:
            return Response(
                {
                    'error': f'drone with id {drone_id} not found'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            drone.name = request.data.get('name', drone.name)
            drone.avg_speed_ms = request.data.get('avg_speed_ms', drone.avg_speed_ms)
            drone.flight_time_seconds = request.data.get('flight_time_seconds', drone.flight_time_seconds)
            drone.save()
            return Response(
                {
                    'data': drone.to_dict()
                },
                status=status.HTTP_200_OK
            )
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
            return Response(
                {
                    'error': 'drone id is required'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        drone = Drone.objects.get(id=drone_id, user=user)
        if not drone:
            return Response(
                {
                    'error': f'drone with id {drone_id} not found!'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        drone.delete()
        return Response(
            {
                'message': f'drone with id {drone_id} deleted!'
            },
            status=status.HTTP_200_OK
        )