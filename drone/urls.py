from django.urls import path

from drone import views

urlpatterns = [
    path('', views.drone_view)
]