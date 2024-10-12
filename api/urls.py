from api import views

from django.urls import path

urlpatterns = [
    path('user/register/', views.user_register),
    path('user/login/', views.user_login),
    path('user-list/', views.user_list),
    path('drone/', views.drone_view)
]
