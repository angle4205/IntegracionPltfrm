from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.authentication.models import Address, Cart

# Create your views here.


def base(request):
    return render(request, "core/base.html")


@login_required
def select_shipping_address(request):
    if request.method == "POST":
        selected_address_id = request.POST.get("selected_address")
        new_address = request.POST.get("new_address")
        set_as_default = request.POST.get("set_as_default")

        if selected_address_id == "pickup":
            # Handle pickup in store
            cart = Cart.objects.get(user=request.user, estado="ACTIVO")
            cart.direccion_envio = None  # No address needed for pickup
            cart.save()
        elif new_address:
            # Handle new address
            address = Address.objects.create(
                user=request.user,
                address=new_address,
                is_default=bool(set_as_default),
            )
            if set_as_default:
                request.user.addresses.update(is_default=False)
                address.is_default = True
                address.save()
            cart = Cart.objects.get(user=request.user, estado="ACTIVO")
            cart.direccion_envio = address
            cart.save()
        elif selected_address_id:
            # Handle existing address
            address = Address.objects.get(id=selected_address_id, user=request.user)
            cart = Cart.objects.get(user=request.user, estado="ACTIVO")
            cart.direccion_envio = address
            cart.save()

        return redirect("authentication:follow_shipping")
