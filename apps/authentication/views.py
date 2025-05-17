from django.contrib.auth import login, logout, authenticate
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
import json
from django.contrib.auth.models import User
from .models import Address, Cart
from django.views.decorators.http import require_POST


def login_view(request):
    if request.method == "POST":
        print("login_view endpoint hit.")
        try:
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                print("Error: Username or password not provided.")
                return JsonResponse(
                    {"error": "Username and password are required."}, status=400
                )

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                print(f"User {user.username} logged in successfully.")
                return JsonResponse({"message": "User authenticated successfully."})
            else:
                print("Invalid credentials.")
                return JsonResponse(
                    {"error": "Invalid username or password."}, status=401
                )
        except Exception as e:
            print("Error in login_view:", str(e))
            return JsonResponse({"error": str(e)}, status=400)

    elif request.method == "GET":
        return render(request, "landing/index.html")

    print("Invalid request method.")
    return JsonResponse({"error": "Invalid request method."}, status=405)


def register_view(request):
    if request.method == "POST":
        print("register_view endpoint hit.")
        try:

            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")
            email = data.get("email", "")

            if not username or not password:
                print("Error: Username or password not provided.")
                return JsonResponse(
                    {"error": "Username and password are required."}, status=400
                )

            if User.objects.filter(username=username).exists():
                print("Error: Username already exists.")
                return JsonResponse({"error": "Username already exists."}, status=400)

            # Crea nuevo usuario
            user = User.objects.create_user(
                username=username, password=password, email=email
            )
            print(f"User {user.username} created successfully.")
            return JsonResponse({"message": "User registered successfully."})

        except Exception as e:
            print("Error in register_view:", str(e))  # Debugging error
            return JsonResponse({"error": str(e)}, status=400)

    print("Invalid request method.")
    return JsonResponse({"error": "Invalid request method."}, status=405)


def logout_view(request):
    if request.method == "POST":
        logout(request)
        return JsonResponse(
            {"message": "User logged out successfully.", "redirect": "/"}
        )
    return JsonResponse({"error": "Invalid request method."}, status=405)


@login_required
def profile(request):
    cart = request.user.carts.filter(
        estado="ABIERTO"
    ).first()  # <-- usa el related_name correcto
    addresses = request.user.addresses.all()  # <-- igual aquí si tienes related_name
    return render(
        request,
        "authentication/profile.html",
        {
            "cart": cart,
            "addresses": addresses,
        },
    )


@login_required
def follow_shipping(request):
    cart = Cart.objects.filter(
        user=request.user, estado__in=["ENVIADO", "ENTREGADO"]
    ).first()
    return render(request, "authentication/follow_shipping.html", {"cart": cart})

@require_POST
@login_required
def select_shipping_address(request):
    try:
        cart = Cart.objects.get(user=request.user, estado="ACTIVO")
        metodo = request.POST.get("selected_address")
        if metodo == "pickup":
            cart.metodo_despacho = "RETIRO_TIENDA"
            cart.direccion_envio = None
            cart.costo_despacho = 0
        else:
            address = Address.objects.get(id=metodo, user=request.user)
            cart.metodo_despacho = "DESPACHO_DOMICILIO"
            cart.direccion_envio = address
            cart.costo_despacho = 2000
        cart.save()
        cart.calcular_totales()
        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@ensure_csrf_cookie
def get_csrf_token(request):
    print("CSRF token set.")
    return JsonResponse({"message": "CSRF token set."})


@login_required
def edit_profile(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user = request.user
            user.first_name = data.get("first_name", "")
            user.last_name = data.get("last_name", "")
            user.email = data.get("email", "")
            user.save()
            return JsonResponse({"message": "Perfil actualizado"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Método no permitido"}, status=405)


@login_required
def edit_photo(request):
    if request.method == "POST":
        try:
            profile = request.user.profile
            if "profile_picture" in request.FILES:
                profile.profile_picture = request.FILES["profile_picture"]
                profile.save()
                return JsonResponse({"message": "Foto actualizada"})
            else:
                return JsonResponse({"error": "No se envió ninguna imagen"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Método no permitido"}, status=405)
