from django.shortcuts import render, get_object_or_404
from .models import Producto


from django.shortcuts import render
from .models import Producto
from django.db.models import Q


def lista_productos(request):
    productos = Producto.objects.all()
    marcas = (
        Producto.objects.order_by("marca").values_list("marca", flat=True).distinct()
    )

    categoria = request.GET.get("categoria")
    if categoria:
        productos = productos.filter(categoria=categoria)

    marca = request.GET.get("marca")
    if marca:
        productos = productos.filter(marca=marca)

    busqueda = request.GET.get("q")
    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda)
            | Q(descripcion__icontains=busqueda)
            | Q(marca__icontains=busqueda)
        )

    orden = request.GET.get("orden")
    if orden == "precio_asc":
        productos = productos.order_by("valor")
    elif orden == "precio_desc":
        productos = productos.order_by("-valor")
    elif orden == "nombre_asc":
        productos = productos.order_by("nombre")
    elif orden == "nombre_desc":
        productos = productos.order_by("-nombre")

    return render(
        request,
        'store/lista_productos.html',
        {
            "productos": productos,
            "marcas": marcas,
            "categorias": Producto.CATEGORIAS_CHOICES,
        },
    )


def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    return render(request, 'store/detalle_producto.html', {"producto": producto})
