from django.urls import path
from . import views

app_name = "authentication"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile, name="profile"),
    path("csrf/", views.get_csrf_token, name="get_csrf_token"),
    path("follow-shipping/", views.follow_shipping, name="follow_shipping"),
]
