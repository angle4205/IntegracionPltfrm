from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, 'landing/index.html')

def about(request):
    return render(request, 'landing/about.html')

def terms_and_conditions(request):
    return render(request, 'terms_and_conditions.html')

def politics(request):
    return render(request, 'politics.html')