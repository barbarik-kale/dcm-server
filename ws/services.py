import json
import logging

from common import utils
from common.utils import decode_jwt_token
from drone.services import DroneService, LiveDataService
from users.services import UserService

DRONE = 'drone'
CONTROLLER = 'controller'

connection_map = dict()
connection_types = ['drone', 'controller']

logger = logging.getLogger('ws')

class DCService:
    """
    DroneControllerService is responsible for validating websocket connection requests, sending messages
    to drones and controllers.
    """
    @staticmethod
    def validate_connection_request(token, connection_type):
        """

        Args:
            token (str) : websocket connection token
            connection_type (str) : type of connection drone or controller

        Returns:
            email (str) : email extracted from token
            drone_id (str) : drone_id extracted from token
            error (str) : error message if any
        """
        if not token:
            return None, None, 'token, drone_id are required'
        if not connection_type in connection_types:
            return None, None, f'connection type must be present in {connection_types}'

        claims = decode_jwt_token(token)
        if not claims:
            return None, None, 'please provide valid token'

        email = claims.get('email', None)
        drone_id = claims.get('drone_id', None)
        if not email or not drone_id:
            return None, None, 'invalid jwt token'

        user = UserService.get_user(email)
        if not user:
            return None, None, f'user with email {email} does not exist'

        drone, error = DroneService.get_drone(email, drone_id)
        if error:
            return None, None, error

        # check for duplicate connection requests
        global connection_map
        details = connection_map.get(drone_id, {
            'drone': None,
            'controller': None
        })
        if details.get(connection_type) is None:
            return email, drone_id, None
        return None, None, f'{connection_type} connection already exists'

    @staticmethod
    def add_drone(drone_id, connection, email=None):
        if not drone_id or not connection:
            return 'drone_id and connection is required'
        global connection_map
        details = connection_map.get(drone_id, None)

        if details and details.get('drone'):
            return 'a drone is already connected'
        if details:
            details['drone'] = connection
        else:
            details = {
                'drone': connection,
                'controller': None
            }
            connection_map[drone_id] = details

        data = {
            'drone_id': str(drone_id),
            'status': 'online'
        }
        DCService.send_to_controller(drone_id, data)

        # set drone online
        LiveDataService.set_online(email, drone_id)
        return None

    @staticmethod
    def add_controller(drone_id, connection):
        if not drone_id or not connection:
            return 'drone_id and connection is required'
        global connection_map
        details = connection_map.get(drone_id, None)

        if details and details.get(CONTROLLER):
            return 'a drone is already connected'
        if details:
            details[CONTROLLER] = connection
        else:
            details = {
                'drone': None,
                'controller': connection
            }
            connection_map[drone_id] = details

        return None

    @staticmethod
    def send_to_drone(drone_id, data):
        global connection_map
        details = connection_map.get(drone_id, None)
        if details and details.get(DRONE):
            drone_connection = details.get(DRONE)
            try:
                drone_connection.send(text_data=json.dumps(data))
            except Exception as e:
                logger.error(msg=f'Exception in send to drone - {e}')
        return None

    @staticmethod
    def send_to_controller(drone_id, data):
        global connection_map
        details = connection_map.get(drone_id, None)
        if details and details.get(CONTROLLER):
            try:
                controller_connection = details.get(CONTROLLER)
                controller_connection.send(text_data=json.dumps(data))
            except Exception as e:
                logger.error(msg=f'Exception in send to drone - {e}')
        return None

    @staticmethod
    def disconnect_drone(drone_id, email=None):
        global connection_map
        details = connection_map.get(drone_id, None)
        if details and details.get(DRONE):
            details[DRONE] = None
            data = {
                'drone_id': str(drone_id),
                'status': 'offline'
            }
            DCService.send_to_controller(drone_id, data)
        LiveDataService.set_offline(email, drone_id)
        return None

    @staticmethod
    def disconnect_controller(drone_id):
        global connection_map
        details = connection_map.get(drone_id, None)
        if details and details.get(CONTROLLER):
            details[CONTROLLER] = None
        return None

    @staticmethod
    def process_message_by_drone(drone_id, text_data, email=None):
        # update live drone data
        try:
            LiveDataService.set_drone_data(email, drone_id, json.loads(text_data))
        except Exception as e:
            logger.error(msg=f'text_data - {text_data}, Exception - {str(e)}')

        global connection_map
        details = connection_map.get(drone_id)
        if details and details.get(CONTROLLER):
            controller_connection = details.get(CONTROLLER)
            try:
                controller_connection.send(text_data=text_data)
            except:
                pass

        return None

    @staticmethod
    def process_message_by_controller(drone_id, text_data):
        global connection_map
        details = connection_map.get(drone_id)
        if details and details.get(DRONE):
            controller_connection = details.get(DRONE)
            try:
                controller_connection.send(text_data=text_data)
            except:
                pass

        return None

    @staticmethod
    def get_drone_status(drone_id):
        global connection_map
        details = connection_map.get(drone_id)
        if details and details.get(DRONE):
            return {
                'status': 'online'
            }
        return {
            'status': 'offline'
        }

    @staticmethod
    def handle_media(drone_id, bytes_data):
        global connection_map
        details = connection_map.get(drone_id)
        if details and details.get(CONTROLLER):
            controller_connection = details.get(CONTROLLER)
            try:
                controller_connection.send(bytes_data=bytes_data)
            except:
                pass


class TokenService:
    @staticmethod
    def get_ws_token(drone_id, email):
        if not email or not drone_id:
            return None, 'drone_id and email are required!'

        drone, error = DroneService.get_drone(email, drone_id)
        if error:
            return None, error

        claims = {
            'email': email,
            'drone_id': str(drone_id)
        }
        token = utils.get_jwt_token(claims, True)
        return token, None