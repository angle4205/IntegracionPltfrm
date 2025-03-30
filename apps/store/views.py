from django.shortcuts import render, get_object_or_404
from django.urls import path
from . import views
from .models import Producto
# Create your views here.

def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'catalogo/lista_productos.html', {'productos': productos})

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    return render(request, 'catalogo/detalle_producto.html', {'producto': producto})