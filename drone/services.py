from uuid import UUID

from django.core.exceptions import ValidationError

from drone.models import Drone
from users.services import UserService


class DroneService:
    @staticmethod
    def get_drone(email, drone_id: UUID):
        try:
            drone = Drone.objects.get(id=drone_id, user__email=email)
            return drone.to_dict()
        except Drone.DoesNotExist:
            return None

    @staticmethod
    def get_drone_list(email):
        if not email:
            return None, 'please provide email'
        drones = Drone.objects.filter(user__email=email)
        drones = [
            drone.to_dict()
            for drone in drones
        ]
        return drones, 'drone list'

    @staticmethod
    def create_drone(email, name, avg_speed_ms, flight_time_seconds):
        if not email:
            return None, 'please provide email'
        user = UserService.get_user(email)
        if not user:
            return None, f'user with email {email} does not exist'
        if not flight_time_seconds:
            return None, 'flight time is required!'

        try:
            drone = Drone(
                name=name,
                avg_speed_ms=avg_speed_ms,
                flight_time_seconds=flight_time_seconds,
                user__id=user.get('id')
            )
            drone.save()
            return drone.to_dict(), 'drone created'
        except ValidationError:
            return None, 'please check required fields'

    @staticmethod
    def update_drone(email, drone_id, details: dict):
        if not email or not drone_id or not details:
            return None, 'please check required details'

        drone = Drone.objects.get(id=drone_id, user__email=email)
        if not drone:
            return None, f'drone with id {drone_id} does not exist'

        try:
            drone.name = details.get('name', drone.name)
            drone.avg_speed_ms = details.get('avg_speed_ms', drone.avg_speed_ms)
            drone.flight_time_seconds = details.get('flight_time_seconds', drone.flight_time_seconds)
            drone.save()
            return drone.to_dict(), 'drone updated'
        except ValidationError:
            return None, 'please check details to be updated'

    @staticmethod
    def delete_drone(email, drone_id):
        if not email or not drone_id:
            return None, 'please provide email and drone_id'

        try:
            drone = Drone.objects.get(id=drone_id, user__email=email)
            drone.delete()
            return True, f'drone with id {drone_id} deleted'
        except Drone.DoesNotExist:
            return False, f'drone with id {drone_id} does not exist'

