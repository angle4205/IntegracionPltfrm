from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path("", views.lista_productos, name="lista_productos"),
    path(
        "producto/<int:producto_id>/", views.detalle_producto, name="detalle_producto"
    ),
    path(
        "agregar-al-carrito/<int:producto_id>/",
        views.agregar_al_carrito,
        name="agregar_al_carrito",
    ),
    path("obtener-carrito/", views.obtener_carrito, name="obtener_carrito"),
    path(
        "obtener-cantidad-carrito/",
        views.obtener_cantidad_carrito,
        name="obtener_cantidad_carrito",
    ),
    path(
        "actualizar-item-carrito/<int:item_id>/",
        views.actualizar_item_carrito,
        name="actualizar_item_carrito",
    ),
    path(
        "eliminar-del-carrito/<int:item_id>/",
        views.eliminar_del_carrito,
        name="eliminar_del_carrito",
    ),
]
