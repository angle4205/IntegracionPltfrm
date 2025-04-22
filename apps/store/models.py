from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
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
    
class Carrito(models.Model):
    session_key = models.CharField(max_length=40, blank=True, null=True)
    METODO_DESPACHO_CHOICES = [
        ('RETIRO_TIENDA', 'Retiro en tienda'),
        ('DESPACHO_DOMICILIO', 'Despacho a domicilio'),
    ]
    
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('PAGADO', 'Pagado'),
        ('EN_PROCESO', 'En proceso'),
        ('ENVIADO', 'Enviado'),
        ('ENTREGADO', 'Entregado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carritos'
    )
    productos = models.ManyToManyField(
        'Producto',
        through='ItemCarrito',
        related_name='carritos'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='ACTIVO'
    )
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    iva = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    metodo_despacho = models.CharField(
        max_length=20,
        choices=METODO_DESPACHO_CHOICES,
        null=True,
        blank=True
    )
    direccion_envio = models.ForeignKey(
        'DireccionEnvio',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    costo_despacho = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    
    class Meta:
        verbose_name = 'Carrito'
        verbose_name_plural = 'Carritos'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f'Carrito #{self.id} - {self.usuario} ({self.estado})'
    
    def calcular_totales(self):
        """Calcula subtotal, IVA y total del carrito"""
        items = self.items.all()
        self.subtotal = sum(item.subtotal() for item in items)
        self.iva = self.subtotal * Decimal('0.19')
        if self.metodo_despacho == 'DESPACHO_DOMICILIO':
            self.total = self.subtotal + self.iva + self.costo_despacho
        else:
            self.total = self.subtotal + self.iva
            self.costo_despacho = Decimal('0')
        
        self.save()
    
    def agregar_producto(self, producto, cantidad=1):
        item, created = ItemCarrito.objects.get_or_create(
            carrito=self,
            producto=producto,
            defaults={'cantidad': cantidad}
        )
        
        if not created:
            item.cantidad += cantidad
            item.save()
        
        self.calcular_totales()
        return item
    
    def remover_producto(self, producto):
        """Elimina un producto del carrito"""
        ItemCarrito.objects.filter(carrito=self, producto=producto).delete()
        self.calcular_totales()
    
    def actualizar_cantidad(self, producto, cantidad):
        """Actualiza la cantidad de un producto en el carrito"""
        if cantidad <= 0:
            return self.remover_producto(producto)
        
        item = ItemCarrito.objects.get(carrito=self, producto=producto)
        item.cantidad = cantidad
        item.save()
        self.calcular_totales()
        return item
    
    def vaciar_carrito(self):
        """Elimina todos los productos del carrito"""
        self.items.all().delete()
        self.subtotal = 0
        self.iva = 0
        self.total = 0
        self.costo_despacho = 0
        self.save()
    
    def actualizar_metodo_despacho(self, metodo, direccion=None):
        """Actualiza el método de despacho y calcula costos"""
        self.metodo_despacho = metodo
        
        if metodo == 'DESPACHO_DOMICILIO':
            self.costo_despacho = Decimal('5000')
            if direccion:
                self.direccion_envio = direccion
        else:
            self.costo_despacho = Decimal('0')
            self.direccion_envio = None
        
        self.calcular_totales()
        self.save()


class ItemCarrito(models.Model):
    carrito = models.ForeignKey(
        'Carrito',
        on_delete=models.CASCADE,
        related_name='items'
    )
    producto = models.ForeignKey(
        'Producto',
        on_delete=models.CASCADE,
        related_name='items_carrito'
    )
    cantidad = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('carrito', 'producto')
        verbose_name = 'Item de carrito'
        verbose_name_plural = 'Items de carrito'
    
    def __str__(self):
        return f'{self.cantidad} x {self.producto.nombre} en carrito #{self.carrito.id}'
    
    def save(self, *args, **kwargs):
        if not self.precio_unitario or self.precio_unitario != self.producto.valor:
            self.precio_unitario = self.producto.valor
        super().save(*args, **kwargs)
    
    def subtotal(self):
        return self.precio_unitario * self.cantidad


class DireccionEnvio(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='direcciones_envio'
    )
    calle = models.CharField(max_length=255)
    numero = models.CharField(max_length=20)
    departamento = models.CharField(max_length=50, blank=True, null=True)
    comuna = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=20, blank=True, null=True)
    indicaciones = models.TextField(blank=True, null=True)
    principal = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Dirección de envío'
        verbose_name_plural = 'Direcciones de envío'
        ordering = ['-principal', 'id']
    
    def __str__(self):
        return f'{self.calle} {self.numero}, {self.comuna}, {self.ciudad}'
    
    def save(self, *args, **kwargs):
        if self.principal:
            DireccionEnvio.objects.filter(usuario=self.usuario, principal=True).update(principal=False)
        super().save(*args, **kwargs)
