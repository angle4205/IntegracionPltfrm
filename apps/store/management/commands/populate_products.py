import os
import random
from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.store.models import Producto, ImagenProducto

class Command(BaseCommand):
    help = 'Generates placeholder products for testing'

    def handle(self, *args, **kwargs):
        # Make sure these match exactly with your CATEGORIAS_CHOICES
        CATEGORY_CODES = [
            "HERRAMIENTAS_MANUALES",
            "HERRAMIENTAS_ELECTRICAS",
            "PINTURAS",
            "MATERIALES_ELECTRICOS",
            "SEGURIDAD",
            "FIJACION",
            "FERRETERIA",
            "JARDIN"
        ]

        # Product data templates - now complete for all categories
        brands = {
            "HERRAMIENTAS_MANUALES": ["Stanley", "Truper", "Irwin", "Bahco", "Fiskars"],
            "HERRAMIENTAS_ELECTRICAS": ["Black & Decker", "Makita", "Bosch", "Dewalt", "Skil"],
            "PINTURAS": ["Suvinil", "Alba", "Sherwin-Williams", "Tersuave", "Colorín"],
            "MATERIALES_ELECTRICOS": ["Philips", "Osram", "Sica", "Pirelli", "Casa Roy"],
            "SEGURIDAD": ["3M", "Honeywell", "DuPont", "Protector", "Segur"],
            "FIJACION": ["Tornillos SRL", "Fijate", "Remachate", "Bulonería Express", "Anclajes Pro"],
            "FERRETERIA": ["Ferremax", "El Martillo", "TodoFierro", "FerreCenter", "Manuelita"],
            "JARDIN": ["Gardena", "Toro", "Husqvarna", "MTD", "Ryobi"]
        }

        product_templates = {
            "HERRAMIENTAS_MANUALES": [
                "Martillo {} g", "Destornillador {}", "Alicate {}", "Llave {}", 
                "Cincel {} mm", "Serrucho {}", "Nivel {} cm", "Pinza {}",
                "Cuchara de albañil", "Pala {}"
            ],
            "HERRAMIENTAS_ELECTRICAS": [
                "Taladro {}", "Amoladora {}", "Sierra caladora {}", "Lijadora {}", 
                "Rotomartillo {}", "Atornillador {}", "Fresadora {}", "Esmeril {}",
                "Pulidora {}", "Soldadora {}"
            ],
            "PINTURAS": [
                "Pintura latex {} L", "Esmalte sintético {} L", "Barniz {} L", 
                "Impermeabilizante {} L", "Pintura epoxi {} kg", "Tinta {} mL",
                "Aerosol color {}", "Pintura antihongos {} L", "Pintura para metal {} L",
                "Protector de madera {} L"
            ],
            "MATERIALES_ELECTRICOS": [
                "Cable {} mm²", "Interruptor {}", "Toma corriente {}", 
                "Portalámpara {}", "Fusible {} A", "Caja de derivación {}",
                "Breaker {}", "Timer digital {}", "Sensor {}", "Transformador {} V"
            ],
            "SEGURIDAD": [
                "Casco {}", "Guantes {}", "Anteojos {}", "Mascarilla {}", 
                "Arnés {}", "Botas {}", "Chaleco reflectante", "Protección auditiva {}",
                "Manga ignífuga", "Extintor {} kg"
            ],
            "FIJACION": [
                "Tornillo {} mm", "Clavo {} mm", "Ancla {} mm", "Remache {} mm",
                "Tarugo {} mm", "Perno {} mm", "Abrazadera {} mm", "Grapa {}",
                "Soporte {}", "Sujetador {}"
            ],
            "FERRETERIA": [
                "Candado {}", "Cadena {} m", "Bisagra {}", "Cerrojo {}", 
                "Cerradura {}", "Llave {}", "Grifo {}", "Válvula {}",
                "Cinta métrica {} m", "Escuadra {}"
            ],
            "JARDIN": [
                "Manguera {} m", "Regador {}", "Cortadora de césped {}", 
                "Podadora {}", "Tijera de podar {}", "Carretilla {}",
                "Rastrillo {}", "Pala de jardín", "Hidrolavadora {}", 
                "Aspersor {}"
            ]
        }

        sizes = {
            "HERRAMIENTAS_MANUALES": ["300", "500", "800", "1000", "1200"],
            "HERRAMIENTAS_ELECTRICAS": ["600W", "800W", "1000W", "1200W", "1500W"],
            "PINTURAS": ["1", "4", "10", "20"],
            "MATERIALES_ELECTRICOS": ["1.5", "2.5", "4", "6", "10"],
            "SEGURIDAD": ["industrial", "básico", "profesional", "premium"],
            "FIJACION": ["3", "4", "5", "6", "8", "10"],
            "FERRETERIA": ["pequeño", "mediano", "grande", "extra grande"],
            "JARDIN": ["5", "10", "15", "20", "25"]
        }

        colors = ["Rojo", "Azul", "Verde", "Amarillo", "Negro", "Blanco", "Gris", "Naranja"]

        # Create products
        for cat_code in CATEGORY_CODES:
            self.stdout.write(f"Creating {cat_code} products...")
            
            for i in range(20):  # Create 20 products per category
                try:
                    brand = random.choice(brands[cat_code])
                    template = random.choice(product_templates[cat_code])
                    
                    # Generate product name
                    if "{}" in template:
                        name = template.format(random.choice(sizes[cat_code]))
                    else:
                        name = template
                    
                    # Add color sometimes
                    if random.random() > 0.7:
                        name = f"{name} {random.choice(colors)}"
                    
                    # Create product
                    product = Producto(
                        marca=brand,
                        nombre=name,
                        categoria=cat_code,
                        valor=random.randint(500, 50000) / 100,
                        stock=random.randint(0, 100),
                        descripcion=f"Producto {name} de la marca {brand}. Ideal para uso {random.choice(['doméstico', 'profesional', 'industrial'])}."
                    )
                    
                    product.save()
                    product.disponible = product.stock > 0
                    product.save()
                    
                    self.stdout.write(f"Created: {product.nombre}")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error creating product: {e}"))
                    continue

        self.stdout.write(self.style.SUCCESS('Successfully created placeholder products'))