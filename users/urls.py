from django.urls import path

from users import views

"""
Auth module has a prefix - user
register/ -> user/register/
"""
urlpatterns = [
    path('register/', views.user_register),
    path('login/', views.user_login),
    path('user-list/', views.user_list),
    path('home/', views.live_video_stream)
]