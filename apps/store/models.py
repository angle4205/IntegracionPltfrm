from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
import os
import random


def generar_nro_referencia_unico():
    while True:
        nro_referencia = str(random.randint(100000, 999999))
        if not Producto.objects.filter(nro_referencia=nro_referencia).exists():
            return nro_referencia


def upload_to(instance, filename):
    return os.path.join("productos", instance.marca, instance.nombre, filename)


class Producto(models.Model):
    CATEGORIAS_CHOICES = [
        ("HERRAMIENTAS_MANUALES", "Herramientas Manuales"),
        ("HERRAMIENTAS_ELECTRICAS", "Herramientas Eléctricas"),
        ("PINTURAS", "Pinturas"),
        ("MATERIALES_ELECTRICOS", "Materiales Eléctricos"),
        ("SEGURIDAD", "Artículos de Seguridad"),
        ("FIJACION", "Artículos de Fijación"),
        ("FERRETERIA", "Ferretería General"),
        ("JARDIN", "Jardín y Exteriores"),
    ]

    marca = models.CharField(max_length=100)
    nombre = models.CharField(max_length=200)

    categoria = models.CharField(
        max_length=50,
        choices=CATEGORIAS_CHOICES,
        default="FERRETERIA",
        verbose_name="Categoría del producto",
    )

    nro_referencia = models.CharField(
        max_length=6, unique=True, default=generar_nro_referencia_unico, editable=False
    )

    valor = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    stock = models.PositiveIntegerField(default=0)

    disponible = models.BooleanField(default=True, editable=False)

    imagen_principal = models.ImageField(
        upload_to=upload_to, blank=True, null=True, verbose_name="Imagen principal"
    )
    imagenes_secundarias = models.ManyToManyField(
        "ImagenProducto", blank=True, related_name="productos"
    )

    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        self.disponible = self.stock > 0

        if not self.nro_referencia:
            self.nro_referencia = generar_nro_referencia_unico()

        super().save(*args, **kwargs)

    def reducir_stock(self, cantidad):

        if cantidad <= self.stock:
            self.stock -= cantidad
            self.save()
            return True
        return False

    def __str__(self):
        return f"{self.nombre} - {self.marca} (Ref: {self.nro_referencia})"


class ImagenProducto(models.Model):

    imagen = models.ImageField(upload_to="productos/secundarias/")

    def __str__(self):
        return f"Imagen ID: {self.id}"
