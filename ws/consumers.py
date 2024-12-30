from urllib.parse import parse_qs

from channels.generic.websocket import WebsocketConsumer

from ws.services import DCService, MediaService


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
        query_string = self.scope['query_string'].decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        email, drone_id, error = DCService.validate_connection_request(token, 'drone')
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
        query_string = self.scope['query_string'].decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        email, drone_id, error = DCService.validate_connection_request(token, 'controller')
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


class MediaProducer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.email = None
        self.drone_id = None

    def connect(self):
        query_string = self.scope['query_string'].decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        email, drone_id, error = MediaService.validate_connection_request(token, 'producer')
        if error:
            self.close(code=404, reason=error)
            return

        res, error = MediaService.add_producer(email, drone_id, self)
        if error:
            self.close(code=404, reason=error)
            return

        self.email = email
        self.drone_id = drone_id
        self.accept()


    def disconnect(self, code):
        MediaService.remove_producer(self.drone_id)


    def receive(self, text_data=None, bytes_data=None):
        MediaService.handle_media_by_producer(self.drone_id, bytes_data)

class MediaConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.email = None
        self.drone_id = None

    def connect(self):
        query_string = self.scope['query_string'].decode()
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        email, drone_id, error = MediaService.validate_connection_request(token, 'consumer')
        if error:
            self.close(code=404, reason=error)
            return

        res, error = MediaService.add_consumer(email, drone_id, self)
        if error:
            self.close(code=404, reason=error)
            return

        self.email = email
        self.drone_id = drone_id
        self.accept()


    def disconnect(self, code):
        MediaService.remove_consumer(self.email, self.drone_id, self)


    def receive(self, text_data=None, bytes_data=None):
        pass
