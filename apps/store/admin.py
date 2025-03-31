from django.contrib import admin
from .models import Producto, ImagenProducto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "marca",
        "categoria",
        "nro_referencia",
        "valor",
        "stock",
        "disponible",
    )
    list_filter = ("categoria", "marca", "disponible")
    readonly_fields = ("disponible", "nro_referencia") 
    search_fields = ("nombre", "marca", "nro_referencia")


@admin.register(ImagenProducto)
class ImagenProductoAdmin(admin.ModelAdmin):
    list_display = ("id", "imagen_preview")

    def imagen_preview(self, obj):
        from django.utils.html import mark_safe

        return mark_safe(f'<img src="{obj.imagen.url}" width="100" />')

    imagen_preview.short_description = "Vista previa"
