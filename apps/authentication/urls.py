from django.urls import path
from . import views

urlpatterns = [
    path("firebase-login/", views.firebase_login, name="firebase_login"),
    path("logout/", views.custom_logout, name="logout"),
    path("profile/", views.profile, name="profile"),
    path("auth/get-csrf-token/", views.get_csrf_token, name="get_csrf_token"),
]