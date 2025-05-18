from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path(
        "select-shipping/",
        views.select_shipping_address,
        name="select_shipping_address",
    ),
    path("create-checkout-session/", views.create_checkout_session, name="create-checkout-session"),
]
