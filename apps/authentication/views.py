from django.contrib.auth import login, logout
from django.http import JsonResponse
from firebase_admin import auth as firebase_auth
from django.contrib.auth.models import User
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
import json


def firebase_login(request):
    if request.method == "POST":
        print("firebase_login endpoint hit.")  # Debugging endpoint hit
        try:
            # Parse the request body
            data = json.loads(request.body)
            token = data.get("token")
            if not token:
                print("Error: Token not provided.")
                return JsonResponse({"error": "Token not provided."}, status=400)

            # Verify the Firebase token
            decoded_token = firebase_auth.verify_id_token(token)
            print("Decoded token:", decoded_token)  # Debugging decoded token

            # Extract user information from the token
            uid = decoded_token["uid"]
            email = decoded_token.get("email")
            name = decoded_token.get("name", "")
            first_name = name.split(" ")[0] if name else ""
            last_name = " ".join(name.split(" ")[1:]) if name else ""

            # Get or create a Django user
            user, created = User.objects.get_or_create(
                username=uid,
                defaults={
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                },
            )

            # Update user details if they already exist
            if not created:
                user.first_name = first_name
                user.last_name = last_name
                user.save()

            print(
                f"User {'created' if created else 'updated'}: {user}"
            )  # Debugging user creation

            # Log the user in
            login(request, user)
            print("User logged in successfully.")
            return JsonResponse({"message": "User authenticated successfully."})

        except Exception as e:
            print("Error in firebase_login:", str(e))  # Debugging error
            return JsonResponse({"error": str(e)}, status=400)

    print("Invalid request method.")
    return JsonResponse({"error": "Invalid request method."}, status=405)


def custom_logout(request):
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
