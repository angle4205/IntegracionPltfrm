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
    path("select-shipping-address/", views.select_shipping_address, name="select_shipping_address"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path("edit-photo/", views.edit_photo, name="edit_photo"),
]
