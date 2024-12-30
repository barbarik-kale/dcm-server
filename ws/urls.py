from django.urls import path

from ws import views
from ws.consumers import DroneConsumer, ControllerConsumer, MediaConsumer, MediaProducer

websocket_urlpatterns = [
    path('ws/drone/', DroneConsumer.as_asgi()),
    path('ws/controller/', ControllerConsumer.as_asgi()),
    path('ws/media/consumer/', MediaConsumer.as_asgi()),
    path('ws/media/producer/', MediaProducer.as_asgi())
]

urlpatterns = [
    path('token/', views.get_ws_token)
]