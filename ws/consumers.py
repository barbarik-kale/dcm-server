import json
from urllib.parse import parse_qs

from channels.generic.websocket import WebsocketConsumer

from common.utils import decode_jwt_token
from drone.services import DroneService
from users.services import UserService

"""
stores mapping of drone_id and details about connections
store = {
    'some_id': {
        'drone': connection,
        'controller': connection
    }
}
"""
store = dict()

class DroneConsumer(WebsocketConsumer):
    """
    A drone establishes websocket connection to push location and other data.
    Also control commands are sent to this websocket connection.

    Headers:
        Authorization: jwt token

    Params:
        drone-id: id of drone

    """

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.email = None
        self.drone_id = None

    def connect(self):
        global store
        headers = dict(self.scope['headers'])
        auth_header = headers.get(b'authorization', None)

        query_string = self.scope['query_string'].decode()
        query_params = parse_qs(query_string)
        drone_id = query_params.get('drone_id', [None])[0]

        if not auth_header or not drone_id:
            self.close(code=404, reason='please include token in header and drone_id in query param')
            return

        claims = decode_jwt_token(auth_header)
        if not claims:
            self.close(code=403, reason='invalid token!')
            return

        email = claims.get('email', None)
        user = UserService.get_user(email)
        if not user:
            self.close(code=404, reason=f'user with email {email} does not exist')
            return

        drone = DroneService.get_drone(email, drone_id)
        if not drone:
            self.close(code=404, reason=f'drone with id {drone_id} does not exist')
            return

        self.email = email
        self.drone_id = drone_id

        details = store.get(drone_id, {
            'drone': None,
            'controller': None
        })

        if details.get('drone'):
            self.close(code=404, reason=f'a drone is already connected with drone id {drone_id}')
            return

        details['drone'] = self
        store[drone_id] = details
        self.accept()

        controller_connection = details['controller']
        if controller_connection:
            data = {
                'drone_id': self.drone_id,
                'status': 'online'
            }
            try:
                controller_connection.send(text_data=json.dumps(data))
            except:
                pass


    def disconnect(self, code):
        global store
        details = store.get(self.drone_id)
        details['drone'] = None

        controller_connection = details['controller']
        if controller_connection:
            data = {
                'drone_id': self.drone_id,
                'status': 'offline'
            }
            controller_connection.send(text_data=json.dumps(data))

    def receive(self, text_data=None, bytes_data=None):
        global store
        details = store.get(self.drone_id)
        controller_connection = details.get('controller')

        try:
            controller_connection.send(text_data, bytes_data)
        except:
            details['controller'] = None


class ControllerConsumer(WebsocketConsumer):
    """
    A controller device (mobile, web or controller) established websocket connection to push control commands
    and pull location and other data.

    Headers:
        Authorization: jwt token

    Params:
        drone-id: id of drone

    """
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.email = None
        self.drone_id = None

    def connect(self):
        global store
        headers = dict(self.scope['headers'])
        auth_header = headers.get(b'authorization', None)

        query_string = self.scope['query_string'].decode()
        query_params = parse_qs(query_string)
        drone_id = query_params.get('drone_id', [None])[0]

        if not auth_header or not drone_id:
            self.close(code=404, reason='please include token in header and drone_id in query param')
            return

        claims = decode_jwt_token(auth_header)
        if not claims:
            self.close(code=403, reason='invalid token!')
            return

        email = claims.get('email', None)
        user = UserService.get_user(email)
        if not user:
            self.close(code=404, reason=f'user with email {email} does not exist')
            return

        drone = DroneService.get_drone(email, drone_id)
        if not drone:
            self.close(code=404, reason=f'drone with id {drone_id} does not exist')
            return

        self.email = email
        self.drone_id = drone_id

        details = store.get(drone_id, {
            'drone': None,
            'controller': None
        })

        if details.get('controller'):
            self.close(code=404, reason=f'a controller is already connected with drone id {drone_id}')
            return

        details['controller'] = self
        store[drone_id] = details
        self.accept()

    def disconnect(self, code):
        global store
        details = store.get(self.drone_id)
        details['controller'] = None


    def receive(self, text_data=None, bytes_data=None):
        global store
        details = store.get(self.drone_id)
        drone_connection = details.get('drone')
        drone_connection.send(text_data=text_data, bytes_data=bytes_data)

