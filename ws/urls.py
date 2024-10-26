from django.urls import path

from ws.consumers import DroneConsumer

websocket_urlpatterns = [
    path('ws/', DroneConsumer.as_asgi())
]