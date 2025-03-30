from django.urls import path
from .views import home
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('terminos-y-condiciones/', views.terms_and_conditions, name='terms_and_conditions'),

]
