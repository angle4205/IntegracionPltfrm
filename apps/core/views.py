from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.authentication.models import Address, Cart
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.conf import settings
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from apps.authentication.models import Cart

# Create your views here.


def base(request):
    return render(
        request,
        "core/base.html",
        {"STRIPE_PUBLISHABLE_KEY": settings.STRIPE_PUBLISHABLE_KEY},
    )


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


@require_POST
@login_required
def create_checkout_session(request):
    try:
        cart = Cart.objects.filter(user=request.user, estado="ACTIVO").first()
        if not cart:
            return JsonResponse({"error": "No hay carrito activo"}, status=400)
        if not hasattr(cart, "items") or not cart.items.exists():
            return JsonResponse({"error": "El carrito está vacío"}, status=400)
        cart.calcular_totales()
        amount = int(cart.total)
        
        if amount <= 0:
            return JsonResponse({"error": "El monto debe ser mayor a 0"}, status=400)

        stripe.api_key = settings.STRIPE_SECRET_KEY

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "clp",
                        "unit_amount": amount,
                        "product_data": {
                            "name": "Compra en Mi Tienda",
                        },
                    },
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url="http://localhost:8000/success/",
            cancel_url="http://localhost:8000/cancel/",
        )
        return JsonResponse({"id": checkout_session.id})
    except Exception as e:
        import traceback

        print(traceback.format_exc())  # Esto te mostrará el error en la consola
        return JsonResponse({"error": str(e)}, status=400)
