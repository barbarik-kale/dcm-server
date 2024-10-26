from channels.generic.websocket import WebsocketConsumer


class DroneConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        print('connected')

    def disconnect(self, code):
        print('disconnected')

    def receive(self, text_data=None, bytes_data=None):
        print(text_data)