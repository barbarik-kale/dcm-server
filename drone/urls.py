from django.urls import path

from drone import views

urlpatterns = [
    path('', views.drone_view),
    path('list/', views.get_drone_list),
    path('live-data/', views.get_drone_live_data)
]