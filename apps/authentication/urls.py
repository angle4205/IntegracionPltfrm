from django.urls import path
from . import views


urlpatterns = [
    path("firebase-login/", views.firebase_login, name="firebase_login"),
    path('profile/', views.profile, name='profile'),
    path("logout/", views.custom_logout, name="logout"),
]