from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.authentication.models import Address, Cart
from django.views.decorators.http import require_POST
from django.http import JsonResponse

# Create your views here.


def base(request):
    return render(request, "core/base.html")


@require_POST
@login_required
def select_shipping_address(request):
    cart = Cart.objects.get(user=request.user, estado="ACTIVO")
    metodo = request.POST.get("selected_address")
    if metodo == "pickup":
        cart.metodo_despacho = "RETIRO_TIENDA"
        cart.direccion_envio = None
        cart.costo_despacho = 0
    elif metodo == "new":
        address_text = request.POST.get("new_address")
        lat = request.POST.get("latitude")
        lon = request.POST.get("longitude")
        if not address_text:
            # Puedes mostrar un mensaje de error si quieres
            return redirect(request.META.get("HTTP_REFERER", "/"))
        nueva_direccion = Address.objects.create(
            user=request.user,
            address=address_text,
            latitude=lat or None,
            longitude=lon or None,
        )
        cart.metodo_despacho = "DESPACHO_DOMICILIO"
        cart.direccion_envio = nueva_direccion
        cart.costo_despacho = 2000
    else:
        address = Address.objects.get(id=metodo, user=request.user)
        cart.metodo_despacho = "DESPACHO_DOMICILIO"
        cart.direccion_envio = address
        cart.costo_despacho = 2000
    cart.save()
    cart.calcular_totales()
    # Redirige a la misma página (donde está el modal)
    return redirect(request.META.get("HTTP_REFERER", "/"))
