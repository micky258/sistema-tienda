from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# CONFIGURACIÓN
import os
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'tienda.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# INICIALIZAR DB
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ---------------- PRODUCTOS ----------------
class Producto(db.Model):
    __tablename__ = "productos"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    detalle = db.Column(db.Text)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    imagen = db.Column(db.String(200), nullable=True)

# ---------------- CLIENTES ----------------
class Cliente(db.Model):
    __tablename__ = "clientes"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    nit_ci = db.Column(db.String(50), nullable=False)

# ---------------- FACTURAS ----------------
class Factura(db.Model):
    __tablename__ = "facturas"

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, unique=True, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False)

    # 🔥 NUEVO (CLAVE)
    subtotal = db.Column(db.Float, default=0.0)
    descuento = db.Column(db.Float, default=0.0)
    gift_card = db.Column(db.Float, default=0.0)

    total = db.Column(db.Float, nullable=False)

    estado = db.Column(db.String(20), default="EMITIDA")
    cuf = db.Column(db.String(100), nullable=True)

    cliente = db.relationship("Cliente", backref="facturas")

    detalles = db.relationship(
        "DetalleFactura",
        backref="factura",
        cascade="all, delete-orphan"
    )

# ---------------- DETALLE FACTURA ----------------
class DetalleFactura(db.Model):
    __tablename__ = "detalles_factura"
    id = db.Column(db.Integer, primary_key=True)
    factura_id = db.Column(db.Integer, db.ForeignKey("facturas.id"), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)

    producto = db.relationship("Producto", backref="detalles_factura")

# ---------------- USUARIO ----------------
class Usuario(db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.String(20), nullable=False)  # admin o vendedor

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

# ---------------- COTIZACION ----------------
class Cotizacion(db.Model):
    __tablename__ = "cotizaciones"

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    descuento = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, nullable=False)
    email = db.Column(db.String(120))
    telefono = db.Column(db.String(50))
    celular = db.Column(db.String(50))
    direccion = db.Column(db.String(200))
    atencion = db.Column(db.String(120))
    version = db.Column(db.Integer, default=1)
    validez = db.Column(db.String(100))
    plazo_entrega = db.Column(db.String(100))
    forma_pago = db.Column(db.String(100))
    observaciones = db.Column(db.Text)
    cliente = db.relationship("Cliente", backref="cotizaciones")
    detalles = db.relationship(
        "DetalleCotizacion",
        backref="cotizacion",
        cascade="all, delete-orphan"   # 👈 agregado
    )
# ---------------- DETALLE COTIZACION ----------------
class DetalleCotizacion(db.Model):
    __tablename__ = "detalles_cotizacion"

    id = db.Column(db.Integer, primary_key=True)
    cotizacion_id = db.Column(db.Integer, db.ForeignKey("cotizaciones.id"), nullable=False)

    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"))
    producto = db.relationship("Producto")

    descripcion = db.Column(db.String(200), nullable=False)
    detalle = db.Column(db.Text)
    imagen = db.Column(db.String(200))

    cantidad = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)


# ---------------- CREAR TABLAS ----------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
