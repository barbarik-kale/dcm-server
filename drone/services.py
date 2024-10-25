from uuid import UUID

from django.core.exceptions import ValidationError

from common.constants import DRONE_LIMIT
from drone.models import Drone
from users.models import User
from users.services import UserService


class DroneService:
    @staticmethod
    def get_drone(email, drone_id: UUID):
        if not email or not drone_id:
            return None, 'please provide valid details!'
        try:
            user = User.objects.get(email=email)
            drone = Drone.objects.get(id=drone_id, user=user)
            return drone, None
        except User.DoesNotExist:
            return None, f'user with email {email} does not exist'
        except Drone.DoesNotExist:
            return None, f'drone with id {drone_id} does not exist'

    @staticmethod
    def get_drone_list(email, user=None):
        if not email:
            return None, 'please provide email'
        if not user:
            user = UserService.get_user(email)
            if not user:
                return None, f'user with email {email} does not exist!'

        drones = Drone.objects.filter(user=user)
        return drones, None

    @staticmethod
    def create_drone(email, name, avg_speed_ms, flight_time_seconds):
        if not email:
            return None, 'please provide email'

        user = UserService.get_user(email)
        if not user:
            return None, f'user with email {email} does not exist'
        if not avg_speed_ms or avg_speed_ms < 0:
            return None, f'avg_speed_ms is missing or invalid'
        if not flight_time_seconds or flight_time_seconds < 0:
            return None, f'flight_time_seconds is missing or invalid'

        try:
            # check the count of drones
            drone_count = Drone.objects.filter(user=user).count()
            if drone_count >= DRONE_LIMIT:
                return None, f'drone creation limit has reached! drone limit is {DRONE_LIMIT}'

            drone = Drone(
                name=name,
                avg_speed_ms=avg_speed_ms,
                flight_time_seconds=flight_time_seconds,
                user=user
            )
            drone.save()
            return drone, None
        except ValidationError:
            return None, 'please check required fields'

    @staticmethod
    def update_drone(email, drone_id, details: dict):
        if not email:
            return None, 'please provide email'
        if not drone_id:
            return None, 'please provide drone id'

        user = UserService.get_user(email)
        if not user:
            return None, f'user with email {email} does not exist'

        drone, error = DroneService.get_drone(email, drone_id)
        if error:
            return None, error

        try:
            # update name, avg_speed_ms, flight_time_seconds
            if details.get('name') is not None:
                drone.name = details.get('name')
            if details.get('avg_speed_ms') is not None:
                speed = details.get('avg_speed_ms')
                if speed < 0:
                    return None, 'avg_speed_ms should be positive'
                drone.avg_speed_ms = speed
            if details.get('flight_time_seconds') is not None:
                flight_time = details.get('flight_time_seconds')
                if flight_time < 0:
                    return None, 'flight_time_seconds should be positive'
                drone.flight_time_seconds = flight_time

            drone.save()
            return drone, None
        except TypeError:
            return None, 'please provide valid details!'
        except ValidationError:
            return None, 'please provide valid details!'

    @staticmethod
    def delete_drone(email, drone_id):
        if not email or not drone_id:
            return None, 'please provide email and drone_id'

        try:
            drone = Drone.objects.get(id=drone_id, user__email=email)
            drone_id = drone.id
            drone.delete()
            return drone_id, None
        except Drone.DoesNotExist:
            return None, f'drone with id {drone_id} does not exist'

