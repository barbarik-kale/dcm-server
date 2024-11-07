from urllib.parse import parse_qs

from channels.generic.websocket import WebsocketConsumer

from ws.services import DCService


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
        headers = dict(self.scope['headers'])
        auth_header = headers.get(b'authorization', None)

        query_string = self.scope['query_string'].decode()
        query_params = parse_qs(query_string)
        drone_id = query_params.get('drone_id', [None])[0]

        email, error = DCService.validate_connection_request(auth_header, drone_id, 'drone')
        if error:
            self.close(code=404, reason=error)
            return

        error = DCService.add_drone(drone_id, self, email)
        if error:
            self.close(code=404, reason=error)
            return

        self.email = email
        self.drone_id = drone_id
        self.accept()

    def disconnect(self, code):
        DCService.disconnect_drone(self.drone_id, self.email)

    def receive(self, text_data=None, bytes_data=None):
        DCService.process_message_by_drone(self.drone_id, text_data, self.email)


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
        headers = dict(self.scope['headers'])
        auth_header = headers.get(b'authorization', None)

        query_string = self.scope['query_string'].decode()
        query_params = parse_qs(query_string)
        drone_id = query_params.get('drone_id', [None])[0]

        email, error = DCService.validate_connection_request(auth_header, drone_id, 'controller')
        if error:
            self.close(code=404, reason=error)
            return

        error = DCService.add_controller(drone_id, self)
        if error:
            self.close(code=404, reason=error)
            return

        self.email = email
        self.drone_id = drone_id
        self.accept()


    def disconnect(self, code):
        DCService.disconnect_controller(self.drone_id)


    def receive(self, text_data=None, bytes_data=None):
        DCService.process_message_by_controller(self.drone_id, text_data)
