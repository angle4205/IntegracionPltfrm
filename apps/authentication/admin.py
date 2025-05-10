from django.contrib import admin
from .models import UserProfile, Address, Cart, ItemCarrito

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "profile_picture")

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "address", "is_default", "latitude", "longitude")

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "updated_at", "estado", "total")

@admin.register(ItemCarrito)
class ItemCarritoAdmin(admin.ModelAdmin):
    list_display = ("carrito", "producto", "cantidad", "precio_unitario", "subtotal")