import sys
import os

# Agregamos la carpeta principal (sistema_tienda) al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, Producto
from app import app
# Lista de productos reales de la empresa
productos_iniciales = [
    {"nombre": "Boquilla de Combustible 3/4\" OPW Rojo", "precio": 962.81, "stock": 10},
    {"nombre": "Boquilla de Combustible 3/4\" OPW Azul", "precio": 962.81, "stock": 10},
    {"nombre": "Boquilla de Combustible 1\" OPW Azul", "precio": 1708, "stock": 10},
    {"nombre": "Codo Giratorio OPW 3/4\" NPT UL", "precio": 683.26, "stock": 10},
    {"nombre": "Codo Giratorio OPW 1\" NPT", "precio": 861.81, "stock": 10},
    {"nombre": "Válvula de Separación OPW 3/4\" NPT UL", "precio": 558.81, "stock": 10},
    {"nombre": "Válvula de Separación OPW 1\" NPT", "precio": 977.95, "stock": 10},
    {"nombre": "Manguera de Combustible 3/4\" (Aistar)", "precio": 100, "stock": 10},
    {"nombre": "Manguera de Combustible 1\" (Aistar)", "precio": 120, "stock": 10},
    {"nombre": "Junta Giratoria 3/4\" NPT", "precio": 120, "stock": 10},
    {"nombre": "Junta Fija 3/4\" NPT", "precio": 100, "stock": 10},
    {"nombre": "Junta Giratoria 1\" NPT", "precio": 160, "stock": 10},
    {"nombre": "Junta Fija 1\" NPT", "precio": 125, "stock": 10},
    {"nombre": "Boquilla de Combustible 3/4\" 11AP Rojo (China)", "precio": 350, "stock": 10},
    {"nombre": "Boquilla de Combustible 3/4\" 11AP Azul (China)", "precio": 350, "stock": 10},
    {"nombre": "Boquilla de Combustible 1\" 7H Azul (China)", "precio": 650, "stock": 10},
    {"nombre": "Codo Giratorio 3/4\" NPT (China)", "precio": 250, "stock": 10},
    {"nombre": "Codo Giratorio 1\" NPT (China)", "precio": 350, "stock": 10},
    {"nombre": "Válvula de Separación 3/4\" NPT (China)", "precio": 250, "stock": 10},
    {"nombre": "Válvula de Separación 1\" NPT (China)", "precio": 350, "stock": 10},
    {"nombre": "Motor Red Jacket Original 1.5 HP", "precio": 17390, "stock": 5},
    {"nombre": "Filtro", "precio": 80, "stock": 20},
    {"nombre": "Mangueras Cortas 3/4\"", "precio": 216, "stock": 15},
    {"nombre": "Mangueras 4m 3/4\"", "precio": 620, "stock": 15},
    {"nombre": "Mangueras Cortas 1\"", "precio": 283.6, "stock": 15},
    {"nombre": "Mangueras 5m 1\"", "precio": 885, "stock": 15},
]

with app.app_context():
    for p in productos_iniciales:
        producto = Producto(nombre=p["nombre"], precio=p["precio"], stock=p["stock"])
        db.session.add(producto)
    db.session.commit()
    print("✅ 26 productos reales cargados correctamente en la base de datos.")