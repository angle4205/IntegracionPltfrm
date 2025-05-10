from django.contrib.auth import login, logout, authenticate
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
import json
from django.contrib.auth.models import User

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
        print("User logged out successfully.")
        return JsonResponse({"message": "User logged out successfully."})
    return JsonResponse({"error": "Invalid request method."}, status=405)


@login_required
def profile(request):
    return render(request, "authentication/profile.html")


@ensure_csrf_cookie
def get_csrf_token(request):
    print("CSRF token set.")
    return JsonResponse({"message": "CSRF token set."})