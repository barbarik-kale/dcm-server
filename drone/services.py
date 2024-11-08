from datetime import datetime
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
    def update_location_details(email, drone_id, latitude, longitude):
        """
        Do not use this service in any api. Only for internal use
        """
        drone, error = DroneService.get_drone(email, drone_id)
        if latitude and longitude:
            drone.last_latitude = latitude
            drone.last_longitude = longitude
        drone.save()


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


drone_data = dict()
class LiveDataService:
    """
    stores drone live data in memory.
    data = {
        'email': 'test@mail.com',
        'latitude': 18.99,
        'longitude': 34.11,
        'last_updated': datetime
    }
    """

    @staticmethod
    def get_drone_data(email, drone_id):
        global drone_data
        data = drone_data.get(str(drone_id), {})
        # if data is stale mark drone as offline
        if data:
            last_updated = data.get('last_update')
            diff = datetime.now() - last_updated
            if diff.seconds > 10:
                data = {}
        if email != data.get('email'):
            data = {}
        return {
            'drone_id': drone_id,
            'latitude': data.get('latitude'),
            'longitude': data.get('longitude'),
            'status': data.get('status', 'offline')
        }

    @staticmethod
    def set_drone_data(email, drone_id, data=None):
        global drone_data
        if data is None:
            data = {}
        if not email or not drone_id:
            return False
        prev_data = drone_data.get(str(drone_id), {})
        drone_data[str(drone_id)] = {
            'email': email,
            'latitude': data.get('latitude', prev_data.get('latitude')),
            'longitude': data.get('longitude', prev_data.get('longitude')),
            'status': data.get('status', prev_data.get('status', 'offline')),
            'last_update': datetime.now()
        }
        return True

    @staticmethod
    def set_online(email, drone_id):
        live_data = {
            'status': 'online'
        }
        LiveDataService.set_drone_data(email, drone_id, live_data)

    @staticmethod
    def set_offline(email, drone_id):
        global drone_data
        live_data = {
            'status': 'offline'
        }
        LiveDataService.set_drone_data(email, drone_id, live_data)

        # update last_latitude and last_longitude
        details = drone_data.get(str(drone_id))
        if details:
            DroneService.update_location_details(
                email,
                drone_id,
                details.get('latitude'),
                details.get('longitude')
            )

    @staticmethod
    def get_drone_data_by_ids(email, drone_ids=None):
        if drone_ids is None:
            drone_ids = []
        data = []
        for drone_id in drone_ids:
            data.append(LiveDataService.get_drone_data(email, drone_id))
        return data

