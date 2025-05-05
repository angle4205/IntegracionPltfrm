from django.contrib.auth import login, logout
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from firebase_admin import auth as firebase_auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def firebase_login(request):
    if request.method == "POST":
        import json

        data = json.loads(request.body)
        token = data.get("token")

        try:
            # Verify the Firebase token
            decoded_token = firebase_auth.verify_id_token(token)
            uid = decoded_token["uid"]
            email = decoded_token.get("email")
            first_name = decoded_token.get("name", "").split(" ")[
                0
            ]  # Extract first name
            last_name = " ".join(
                decoded_token.get("name", "").split(" ")[1:]
            )  # Extract last name

            # Get or create a Django user
            user, created = User.objects.get_or_create(
                username=uid,
                defaults={
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                },
            )

            # Update first_name and last_name if the user already exists
            if not created:
                user.first_name = first_name
                user.last_name = last_name
                user.save()

            login(request, user)  # Log the user in
            return JsonResponse({"message": "User authenticated successfully."})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=405)


def custom_logout(request):
    logout(request)
    return HttpResponseRedirect("/")


@login_required
def profile(request):
    return render(request, "authentication/profile.html")
