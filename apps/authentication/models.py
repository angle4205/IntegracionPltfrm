from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator
from decimal import Decimal


# Usuario extendido
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", blank=True, null=True
    )

    def __str__(self):
        return f"Perfil de {self.user.username}"

    def get_default_address(self):
        default_address = self.user.addresses.filter(is_default=True).first()
        if default_address:
            return f"{default_address.address}"
        return "Sin dirección predeterminada"


# Decoradores para crear y guardar automáticamente el UserProfile
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Crea un UserProfile automáticamente cuando se crea un User."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Guarda el UserProfile automáticamente cuando se guarda un User."""
    instance.profile.save()


# Direccion
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    address = models.TextField()
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"Address for {self.user.username}: {self.address}"


# Carrito
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="carts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    estado = models.CharField(
        max_length=20,
        choices=[
            ("ACTIVO", "Activo"),
            ("PAGADO", "Pagado"),
            ("EN_PROCESO", "En proceso"),
            ("ENVIADO", "Enviado"),
            ("ENTREGADO", "Entregado"),
            ("CANCELADO", "Cancelado"),
        ],
        default="ACTIVO",
    )
    subtotal = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    iva = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    total = models.DecimalField(
        max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)]
    )
    metodo_despacho = models.CharField(
        max_length=20,
        choices=[
            ("RETIRO_TIENDA", "Retiro en tienda"),
            ("DESPACHO_DOMICILIO", "Despacho a domicilio"),
        ],
        null=True,
        blank=True,
    )
    direccion_envio = models.ForeignKey(
        Address, on_delete=models.SET_NULL, null=True, blank=True
    )
    costo_despacho = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    def __str__(self):
        return f"Cart #{self.id} - {self.user.username} ({self.estado})"

    def calcular_totales(self):
        """Calcula subtotal, IVA y total del carrito"""
        items = self.items.all()
        self.subtotal = sum(item.subtotal() for item in items)
        self.iva = self.subtotal * Decimal("0.19")
        if self.metodo_despacho == "DESPACHO_DOMICILIO":
            self.total = self.subtotal + self.iva + self.costo_despacho
        else:
            self.total = self.subtotal + self.iva
            self.costo_despacho = Decimal("0")
        self.save()


# Item Carrito
class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(
        "store.Producto", on_delete=models.CASCADE, related_name="items_carrito"
    )
    cantidad = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )

    def subtotal(self):
        return self.cantidad * self.precio_unitario
