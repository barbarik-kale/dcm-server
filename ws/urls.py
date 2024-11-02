from django.urls import path

from ws.consumers import DroneConsumer, ControllerConsumer

websocket_urlpatterns = [
    path('ws/drone/', DroneConsumer.as_asgi()),
    path('ws/controller/', ControllerConsumer.as_asgi())
]