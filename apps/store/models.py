from django.db import models

# Create your models here.

class Producto(models.Model):
    marca = models.CharField(max_length=100)
    nombre = models.CharField(max_length=200)
    nro_referencia = models.CharField(max_length=50, unique=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    disponible = models.BooleanField(default=True)

    def actualizar_disponibilidad(self, cantidad_seleccionada):

        if self.stock < cantidad_seleccionada:
            self.disponible = False
        else:
            self.disponible = True
        self.save()

    def __str__(self):
        return f"{self.nombre} - {self.marca} ({'Disponible' if self.disponible else 'No Disponible'})"
