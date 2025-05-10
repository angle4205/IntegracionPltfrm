from django.shortcuts import render, get_object_or_404
from .models import Producto
from apps.authentication.models import (
    Cart,
    ItemCarrito,
) 
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from decimal import Decimal
import json


def get_or_create_cart(request):
    """Obtiene o crea un carrito para el usuario autenticado o la sesión."""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user, estado="ACTIVO")
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
        cart, created = Cart.objects.get_or_create(
            session_key=request.session.session_key, estado="ACTIVO"
        )
    return cart


def lista_productos(request):
    productos = Producto.objects.all()
    marcas = (
        Producto.objects.order_by("marca").values_list("marca", flat=True).distinct()
    )

    categoria = request.GET.get("categoria")
    if categoria:
        productos = productos.filter(categoria=categoria)

    marca = request.GET.get("marca")
    if marca:
        productos = productos.filter(marca=marca)

    busqueda = request.GET.get("q")
    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda)
            | Q(descripcion__icontains=busqueda)
            | Q(marca__icontains=busqueda)
        )

    orden = request.GET.get("orden")
    if orden == "precio_asc":
        productos = productos.order_by("valor")
    elif orden == "precio_desc":
        productos = productos.order_by("-valor")
    elif orden == "nombre_asc":
        productos = productos.order_by("nombre")
    elif orden == "nombre_desc":
        productos = productos.order_by("-nombre")

    return render(
        request,
        "store/lista_productos.html",
        {
            "productos": productos,
            "marcas": marcas,
            "categorias": Producto.CATEGORIAS_CHOICES,
        },
    )


def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    return render(request, "store/detalle_producto.html", {"producto": producto})


@require_POST
def agregar_al_carrito(request, producto_id):
    try:
        producto = Producto.objects.get(id=producto_id)
        cart = get_or_create_cart(request)

        item, created = ItemCarrito.objects.get_or_create(
            carrito=cart,
            producto=producto,
            defaults={"cantidad": 1, "precio_unitario": producto.valor},
        )

        if not created:
            item.cantidad += 1
            item.save()

        cart.calcular_totales()

        return JsonResponse({"success": True, "carrito_count": cart.items.count()})
    except Producto.DoesNotExist:
        return JsonResponse(
            {"success": False, "message": "Producto no encontrado"}, status=404
        )
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=400)


def obtener_carrito(request):
    try:
        cart = get_or_create_cart(request)
        items = []

        for item in cart.items.all():
            items.append(
                {
                    "id": item.id,
                    "producto_id": item.producto.id,
                    "nombre": item.producto.nombre,
                    "marca": item.producto.marca,
                    "imagen": (
                        item.producto.imagen_principal.url
                        if item.producto.imagen_principal
                        else ""
                    ),
                    "precio_unitario": float(item.precio_unitario),
                    "cantidad": item.cantidad,
                    "subtotal": float(item.subtotal()),
                }
            )

        return JsonResponse(
            {
                "success": True,
                "items": items,
                "subtotal": float(cart.subtotal),
                "iva": float(cart.iva),
                "costo_despacho": float(cart.costo_despacho),
                "total": float(cart.total),
                "carrito_count": cart.items.count(),
            }
        )
    except Exception as e:
        return JsonResponse(
            {
                "success": True,
                "items": [],
                "subtotal": 0,
                "iva": 0,
                "costo_despacho": 0,
                "total": 0,
                "carrito_count": 0,
                "message": str(e),
            }
        )


def obtener_cantidad_carrito(request):
    try:
        cart = get_or_create_cart(request)
        return JsonResponse({"success": True, "carrito_count": cart.items.count()})
    except Exception as e:
        return JsonResponse({"success": True, "carrito_count": 0, "message": str(e)})


@require_POST
def actualizar_item_carrito(request, item_id):
    try:
        data = json.loads(request.body)
        cantidad = int(data.get("cantidad", 1))

        if cantidad < 1:
            return JsonResponse(
                {"success": False, "message": "Cantidad inválida"}, status=400
            )

        cart = get_or_create_cart(request)
        item = ItemCarrito.objects.get(id=item_id, carrito=cart)
        item.cantidad = cantidad
        item.save()

        cart.calcular_totales()

        return JsonResponse({"success": True, "carrito_count": cart.items.count()})
    except ItemCarrito.DoesNotExist:
        return JsonResponse(
            {"success": False, "message": "Ítem no encontrado"}, status=404
        )
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=400)


@require_POST
def eliminar_del_carrito(request, item_id):
    try:
        cart = get_or_create_cart(request)
        item = ItemCarrito.objects.get(id=item_id, carrito=cart)
        item.delete()

        cart.calcular_totales()

        return JsonResponse({"success": True, "carrito_count": cart.items.count()})
    except ItemCarrito.DoesNotExist:
        return JsonResponse(
            {"success": False, "message": "Ítem no encontrado"}, status=404
        )
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=400)
