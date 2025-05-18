from apps.authentication.models import (
    Cart,
    ItemCarrito,
)
import subprocess 
import stripe
from django.views import View
from django.http import JsonResponse
from django.conf import settings
from django.urls import path
from ..store.views import CreateCheckoutSessionView

stripe.api_key = "pk_test_51RJcP5PIYS2ndJyWc3dC1JdPO33I7lalFrnPLOxcceZjfWr4rU2h17C6ge2xmjK1udqyQOx6FN5jjTLR6UlGHd5G0021Rm2qcc"
# views.py


class CreateCheckoutSessionView(View):
    subprocess.run(["node", "apps/store/static/js/cart.js"])

    def post(self, request, *args, **kwargs):
        YOUR_DOMAIN = "http://localhost:8000"
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'clp',
                            'unit_amount': Cart.calcular_totales,  # variable del total
                            'product_data': {
                                'name': 'Producto ejemplo',
                            },
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=YOUR_DOMAIN + '/success/',
                cancel_url=YOUR_DOMAIN + '/cancel/',
            )
            return JsonResponse({'id': checkout_session.id})
        except Exception as e:
            return JsonResponse({'error': str(e)})
urlpatterns = [

    path('create-checkout-session/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
]
