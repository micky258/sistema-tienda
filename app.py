import os
import io
import math

from flask import Flask, Response, make_response, render_template, request, redirect, url_for, session
from models import db, Producto, Cliente, Factura, DetalleFactura, Usuario, Cotizacion, DetalleCotizacion
from sqlalchemy import func
from datetime import datetime
from config_sin import SinConfig

from flask_migrate import Migrate
from weasyprint import HTML
from num2words import num2words

# ---------------- CONVERTIR NÚMERO A LITERAL ----------------
def numero_a_literal(numero: float) -> str:
    """
    Convierte un número en literal en español, con dos decimales para centavos.
    Ejemplo: 123.45 -> 'CIENTO VEINTITRÉS 45/100 BOLIVIANOS'
    """
    numero = float(numero)

    entero = int(math.floor(numero))
    decimal = int(round((numero - entero) * 100))

    literal = num2words(entero, lang='es').upper()

    return f"{literal} {decimal:02d}/100 BOLIVIANOS"


# ---------------- CONFIGURACIÓN APP ----------------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tienda.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "supersecretkey"

# Inicializar DB y migraciones
db.init_app(app)
migrate = Migrate(app, db)

# 👇 Esto asegura que Flask reconozca tu aplicación
def create_app():
    return app

# ---------------- CREAR TABLAS ----------------
with app.app_context():
    db.create_all()

# ---------------- CARGA AUTOMÁTICA DE PRODUCTOS ----------------
with app.app_context():
    productos_iniciales = [
        {"nombre": "Boquilla de Combustible 3/4\" OPW Rojo", "precio": 962.81, "stock": 10, "imagen": "boquilla_opw_rojo.jpg"},
        {"nombre": "Boquilla de Combustible 3/4\" OPW Azul", "precio": 962.81, "stock": 10, "imagen": "boquilla_opw_azul.jpg"},
        {"nombre": "Boquilla de Combustible 1\" OPW Azul", "precio": 1708, "stock": 10, "imagen": "boquilla_opw_1_azul.jpg"},
        {"nombre": "Codo Giratorio OPW 3/4\" NPT UL", "precio": 683.26, "stock": 10, "imagen": "codo_opw_3_4.jpg"},
        {"nombre": "Codo Giratorio OPW 1\" NPT", "precio": 861.81, "stock": 10, "imagen": "codo_opw_1.jpg"},
        {"nombre": "Válvula de Separación OPW 3/4\" NPT UL", "precio": 558.81, "stock": 10, "imagen": "valvula_opw_3_4.jpg"},
        {"nombre": "Válvula de Separación OPW 1\" NPT", "precio": 977.95, "stock": 10, "imagen": "valvula_opw_1.jpg"},
        {"nombre": "Manguera de Combustible 3/4\" (Aistar)", "precio": 100, "stock": 10, "imagen": "manguera_aistar_3_4.jpg"},
        {"nombre": "Manguera de Combustible 1\" (Aistar)", "precio": 120, "stock": 10, "imagen": "manguera_aistar_1.jpg"},
        {"nombre": "Junta Giratoria 3/4\" NPT", "precio": 120, "stock": 10, "imagen": "junta_giratoria_3_4.jpg"},
        {"nombre": "Junta Fija 3/4\" NPT", "precio": 100, "stock": 10, "imagen": "junta_fija_3_4.jpg"},
        {"nombre": "Junta Giratoria 1\" NPT", "precio": 160, "stock": 10, "imagen": "junta_giratoria_1.jpg"},
        {"nombre": "Junta Fija 1\" NPT", "precio": 125, "stock": 10, "imagen": "junta_fija_1.jpg"},
        {"nombre": "Boquilla de Combustible 3/4\" 11AP Rojo (China)", "precio": 350, "stock": 10, "imagen": "boquilla_china_rojo.jpg"},
        {"nombre": "Boquilla de Combustible 3/4\" 11AP Azul (China)", "precio": 350, "stock": 10, "imagen": "boquilla_china_azul.jpg"},
        {"nombre": "Boquilla de Combustible 1\" 7H Azul (China)", "precio": 650, "stock": 10, "imagen": "boquilla_china_1_azul.jpg"},
        {"nombre": "Codo Giratorio 3/4\" NPT (China)", "precio": 250, "stock": 10, "imagen": "codo_china_3_4.jpg"},
        {"nombre": "Codo Giratorio 1\" NPT (China)", "precio": 350, "stock": 10, "imagen": "codo_china_1.jpg"},
        {"nombre": "Válvula de Separación 3/4\" NPT (China)", "precio": 250, "stock": 10, "imagen": "valvula_china_3_4.jpg"},
        {"nombre": "Válvula de Separación 1\" NPT (China)", "precio": 350, "stock": 10, "imagen": "valvula_china_1.jpg"},
        {"nombre": "Motor Red Jacket Original 1.5 HP", "precio": 17390, "stock": 5, "imagen": "motor_red_jacket.jpg"},
        {"nombre": "Filtro", "precio": 80, "stock": 20, "imagen": "filtro.jpg"},
        {"nombre": "Mangueras Cortas 3/4\"", "precio": 216, "stock": 15, "imagen": "manguera_corta_3_4.jpg"},
        {"nombre": "Mangueras 4m 3/4\"", "precio": 620, "stock": 15, "imagen": "manguera_4m_3_4.jpg"},
        {"nombre": "Mangueras Cortas 1\"", "precio": 283.6, "stock": 15, "imagen": "manguera_corta_1.jpg"},
        {"nombre": "Mangueras 5m 1\"", "precio": 885, "stock": 15, "imagen": "manguera_5m_1.jpg"},
        {"nombre": "Dispensador de Combustible RT-C122 Diesel", "precio": 61572.00, "stock": 4, "imagen": "dispensador_rt_c122_diesel.jpg"},
        {"nombre": "Dispensador de Combustible RT-C122 Gasolina", "precio": 58151.00, "stock": 5, "imagen": "dispensador_rt_c122_gasolina.jpg"},
        {"nombre": "Dispensador de Combustible RT-C242 Diesel/Gasolina", "precio": 89454.00, "stock": 2, "imagen": "dispensador_rt_c242.jpg"},
        {"nombre": "Dispensador de Combustible RT-C244 Gasolina Alto Caudal", "precio": 104485.00, "stock": 1, "imagen": "dispensador_rt_c244.jpg"},
        {"nombre": "Fuel Dispenser RT-M111 Surtidor Móvil", "precio": 33895.00, "stock": 1, "imagen": "fuel_dispenser_rt_m111.jpg"},
        {"nombre": "Motor EX 380V 50HZ 2.2KW Vane Pump YB-50", "precio": 29542.00, "stock": 1, "imagen": "motor_ex_380v.jpg"},
        {"nombre": "Motor EX 220V 50HZ 2.2KW Vane Pump YB-50", "precio": 44435.00, "stock": 1, "imagen": "motor_ex_220v.jpg"},
        {"nombre": "Submersible Pump Electromotor 1.5 HP", "precio": 10883.00, "stock": 10, "imagen": "submersible_pump_1_5hp.jpg"},
        {"nombre": "Submersible Pump Electromotor 2 HP", "precio": 13993.00, "stock": 2, "imagen": "submersible_pump_2hp.jpg"},
        {"nombre": "Submersible Pump Head 2 HP", "precio": 12993.00, "stock": 5, "imagen": "submersible_pump_head_2hp.jpg"},
    ]

    for p in productos_iniciales:
        existente = Producto.query.filter_by(nombre=p["nombre"]).first()
        if not existente:
            producto = Producto(
                nombre=p["nombre"],
                precio=p["precio"],
                stock=p["stock"],
                imagen=p["imagen"]
            )
            db.session.add(producto)
    db.session.commit()
    print("✅ Productos iniciales cargados o actualizados sin duplicar.")

# ---------------- INICIO ----------------
@app.route("/")
def index():
    return redirect(url_for("pos"))

# ---------------- PRODUCTOS ----------------
@app.route("/productos", methods=["GET", "POST"])
def productos():
    if "rol" not in session or session["rol"] != "admin":
        return redirect(url_for("pos"))

    if request.method == "POST":
        nombre = request.form["nombre"]
        precio = float(request.form["precio"])
        stock = int(request.form["stock"])

        imagen_file = request.files.get("imagen")
        imagen_nombre = None
        if imagen_file and imagen_file.filename != "":
            upload_folder = os.path.join("static", "uploads", "productos")
            os.makedirs(upload_folder, exist_ok=True)
            ruta = os.path.join(upload_folder, imagen_file.filename)
            imagen_file.save(ruta)
            imagen_nombre = imagen_file.filename

        nuevo = Producto(nombre=nombre, precio=precio, stock=stock, imagen=imagen_nombre)
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for("productos"))

    productos = Producto.query.all()
    return render_template("productos.html", productos=productos)


# ---------------- ADMIN PRODUCTOS ----------------
@app.route("/admin/productos")
def admin_productos():
    if "rol" not in session or session["rol"] != "admin":
        return redirect(url_for("pos"))

    productos = Producto.query.all()
    return render_template("admin_productos.html", productos=productos)

@app.route("/admin/productos/editar/<int:id>", methods=["GET", "POST"])
def editar_producto(id):
    if "rol" not in session or session["rol"] != "admin":
        return redirect(url_for("pos"))

    producto = Producto.query.get_or_404(id)

    if request.method == "POST":
        producto.nombre = request.form["nombre"]
        producto.precio = float(request.form["precio"])
        producto.stock = int(request.form["stock"])

        # 👇 SIEMPRE guardar detalle
        producto.detalle = request.form.get("detalle")

        imagen_file = request.files.get("imagen")
        if imagen_file and imagen_file.filename != "":
            upload_folder = os.path.join("static", "uploads", "productos")
            os.makedirs(upload_folder, exist_ok=True)
            ruta = os.path.join(upload_folder, imagen_file.filename)
            imagen_file.save(ruta)
            producto.imagen = imagen_file.filename

        db.session.commit()
        return redirect(url_for("admin_productos"))

    return render_template("editar_producto.html", producto=producto)

@app.route("/admin/productos/eliminar/<int:id>", methods=["POST", "GET"])
def eliminar_producto(id):
    if "rol" not in session or session["rol"] != "admin":
        return redirect(url_for("pos"))

    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    return redirect(url_for("admin_productos"))
# ---------------- POS ----------------
@app.route("/pos", methods=["GET", "POST"])
def pos():
    if "usuario" not in session:
        return redirect(url_for("login"))

    productos = Producto.query.all()

    if "carrito" not in session:
        session["carrito"] = []

    if request.method == "POST":
        producto_id = int(request.form["producto_id"])
        cantidad = int(request.form["cantidad"])

        producto = db.session.get(Producto, producto_id)

        if producto and cantidad > 0 and cantidad <= producto.stock:
            session["carrito"].append({
                "producto_id": producto.id,
                "nombre": producto.nombre,
                "precio": producto.precio,
                "cantidad": cantidad,
                "subtotal": producto.precio * cantidad
            })
            session.modified = True

    total = sum(item["subtotal"] for item in session["carrito"])

    return render_template(
        "pos.html",
        productos=productos,
        carrito=session["carrito"],
        total=total,
        nombre_empresa="RED HUALL"
    )
# ---------------- ELIMINAR ITEM DEL CARRITO ----------------
@app.route("/eliminar_item/<int:producto_id>", methods=["POST"])
def eliminar_item(producto_id):
    if "carrito" in session:
        # Filtrar el carrito quitando el producto con ese ID
        session["carrito"] = [
            item for item in session["carrito"] if item["producto_id"] != producto_id
        ]
        session.modified = True
    return redirect(url_for("pos"))
# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        usuario = Usuario.query.filter_by(username=username).first()

        if usuario and usuario.check_password(password):
            session["usuario"] = usuario.username
            session["rol"] = usuario.rol
            return redirect(url_for("pos"))
        else:
            return render_template("login.html", error="Credenciales incorrectas")

    return render_template("login.html")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------- CONFIRMAR FACTURA ----------------
@app.route("/confirmar_factura", methods=["POST"])
def confirmar_factura():
    if "carrito" not in session or len(session["carrito"]) == 0:
        return redirect(url_for("pos"))

    nombre = request.form["nombre"]
    nit_ci = request.form["nit_ci"]

    # 🔒 Validación segura
    try:
        descuento = float(request.form.get("descuento") or 0)
        gift_card = float(request.form.get("gift_card") or 0)
    except:
        descuento = 0
        gift_card = 0

    # 🔎 Buscar cliente existente
    cliente = Cliente.query.filter_by(nit_ci=nit_ci).first()
    if not cliente:
        cliente = Cliente(nombre=nombre, nit_ci=nit_ci)
        db.session.add(cliente)
        db.session.commit()

    # 🔢 Número de factura
    numero_factura = (db.session.query(func.max(Factura.numero)).scalar() or 0) + 1

    # 💰 Subtotal original (sin descuento)
    subtotal = sum(item["subtotal"] for item in session["carrito"])

    # 🚨 Validaciones
    if descuento > subtotal:
        descuento = subtotal

    if gift_card > (subtotal - descuento):
        gift_card = subtotal - descuento

    # 🔥 FACTOR DE DESCUENTO PROPORCIONAL
    factor_descuento = 0
    if subtotal > 0:
        factor_descuento = descuento / subtotal

    # 🎯 Redondeo base
    subtotal = round(subtotal, 2)
    descuento = round(descuento, 2)
    gift_card = round(gift_card, 2)

    # 🧾 Crear factura (temporalmente total=0)
    factura = Factura(
        numero=numero_factura,
        cliente_id=cliente.id,
        subtotal=subtotal,
        descuento=descuento,
        gift_card=gift_card,
        total=0,
        fecha=datetime.now()
    )

    db.session.add(factura)
    db.session.commit()

    # 📦 Crear detalles con descuento distribuido
    suma_detalles = 0

    for i, item in enumerate(session["carrito"]):
        producto = db.session.get(Producto, item["producto_id"])

        if not producto:
            continue

        # 🚨 Validar stock
        if producto.stock < item["cantidad"]:
            flash(f"Stock insuficiente para {producto.nombre}", "danger")
            return redirect(url_for("pos"))

        subtotal_original = item["precio"] * item["cantidad"]

        # 🔥 descuento proporcional
        descuento_item = subtotal_original * factor_descuento
        subtotal_final = subtotal_original - descuento_item

        # 🎯 Redondeo
        subtotal_final = round(subtotal_final, 2)

        suma_detalles += subtotal_final

        detalle = DetalleFactura(
            factura_id=factura.id,
            producto_id=producto.id,
            cantidad=item["cantidad"],
            precio_unitario=item["precio"],
            subtotal=subtotal_final
        )

        producto.stock -= item["cantidad"]
        db.session.add(detalle)

    # 🔥 AJUSTE FINAL (evita errores de centavos)
    diferencia = round((subtotal - descuento) - suma_detalles, 2)

    if abs(diferencia) > 0:
        ultimo_detalle = factura.detalles[-1] if factura.detalles else None
        if ultimo_detalle:
            ultimo_detalle.subtotal = round(ultimo_detalle.subtotal + diferencia, 2)

    # 💰 TOTAL FINAL
    total = subtotal - descuento - gift_card

    if total < 0:
        total = 0

    total = round(total, 2)

    factura.total = total

    db.session.commit()

    # 🧹 Limpiar carrito
    session["carrito"] = []
    session.modified = True

    # ✅ Mensaje
    flash("✅ Factura generada correctamente (modo profesional)", "success")

    return redirect(url_for("facturas"))


# ---------------- LISTA FACTURAS ----------------
@app.route("/facturas")
def facturas():
    facturas = Factura.query.order_by(Factura.id.desc()).all()
    return render_template("facturas.html", facturas=facturas)


# ---------------- VER FACTURA ----------------
@app.route("/ver_factura/<int:factura_id>")
def ver_factura(factura_id):
    factura = db.session.get(Factura, factura_id)
    if not factura:
        return redirect(url_for("facturas"))

    total_literal = numero_a_literal(float(factura.total))

    return render_template(
        "ver_factura.html",
        empresa=SinConfig.RAZON_SOCIAL,
        nit=SinConfig.NIT,
        numero=factura.numero,
        fecha=factura.fecha.strftime("%d/%m/%Y %H:%M"),
        cliente=factura.cliente.nombre,
        nit_ci=factura.cliente.nit_ci,
        detalles=factura.detalles,
        total=factura.total,
        total_literal=total_literal,
        cuf=factura.cuf,
        factura=factura
    )

# ---------------- DESCARGAR PDF----------------
@app.route("/descargar_factura/<int:factura_id>")
def descargar_factura(factura_id):
    factura = db.session.get(Factura, factura_id)
    if not factura:
        return redirect(url_for("facturas"))

    total_literal = numero_a_literal(float(factura.total))

    # Rutas absolutas para logo y QR
    logo_url = url_for('static', filename='logo.png', _external=True)
    qr_url = url_for('static', filename='qr_ficticio.png', _external=True)

    # Renderizar plantilla HTML con el mismo formato que la página
    html = render_template(
        "ver_factura.html",
        empresa=SinConfig.RAZON_SOCIAL,
        nit=SinConfig.NIT,
        numero=factura.numero,
        fecha=factura.fecha.strftime("%d/%m/%Y %H:%M"),
        cliente=factura.cliente.nombre,
        nit_ci=factura.cliente.nit_ci,
        detalles=factura.detalles,
        total=factura.total,
        total_literal=total_literal,
        cuf=factura.cuf,
        factura=factura,
        logo_url=logo_url,
        qr_url=qr_url
    )

    pdf = HTML(string=html).write_pdf()

    # 🔹 Construir nombre profesional del archivo
    fecha_str = factura.fecha.strftime("%Y%m%d")
    cliente_str = factura.cliente.nombre.replace(" ", "_")
    filename = f"Factura-REDHUALL-{factura.numero}-{cliente_str}-{fecha_str}.pdf"

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return response
# ---------------- LISTA COTIZACIONES ----------------
@app.route("/cotizaciones")
def cotizaciones():
    cotizaciones = Cotizacion.query.order_by(Cotizacion.id.desc()).all()
    return render_template("cotizaciones.html", cotizaciones=cotizaciones)
# ---------------- NUEVA COTIZACION ----------------
@app.route("/nueva_cotizacion", methods=["GET", "POST"])
def nueva_cotizacion():
    if request.method == "POST":
        import json

        # =========================
        # DATOS CLIENTE
        # =========================
        cliente_nombre = request.form["cliente_nombre"]
        cliente_nit = request.form["cliente_nit"]

        email = request.form.get("cliente_email")
        celular = request.form.get("cliente_celular")
        direccion = request.form.get("cliente_direccion")
        telefono = request.form.get("cliente_telefono")
        atencion = request.form.get("cliente_atencion")

        # =========================
        # CONDICIONES
        # =========================
        validez = request.form.get("validez")
        plazo_entrega = request.form.get("plazo_entrega")
        forma_pago = request.form.get("forma_pago")
        observaciones = request.form.get("observaciones")

        # =========================
        # CLIENTE
        # =========================
        cliente = Cliente.query.filter_by(nit_ci=cliente_nit).first()
        if not cliente:
            cliente = Cliente(nombre=cliente_nombre, nit_ci=cliente_nit)
            db.session.add(cliente)
            db.session.commit()

        # =========================
        # NUMERO COTIZACION
        # =========================
        ultima = db.session.query(Cotizacion).order_by(Cotizacion.id.desc()).first()

        if ultima and ultima.numero:
            nuevo_numero = int(ultima.numero) + 1
        else:
            nuevo_numero = 1

        numero_cotizacion = str(nuevo_numero).zfill(4)

        # =========================
        # PRODUCTOS
        # =========================
        productos_json = request.form.get("productos_json")
        productos_seleccionados = json.loads(productos_json)

        subtotal = sum(p["precio"] * p["cantidad"] for p in productos_seleccionados)
        descuento = 0
        total = subtotal - descuento

        # =========================
        # CREAR COTIZACION
        # =========================
        cotizacion = Cotizacion(
            numero=numero_cotizacion,
            fecha=datetime.now(),
            cliente_id=cliente.id,
            subtotal=subtotal,
            descuento=descuento,
            total=total,
            email=email,
            celular=celular,
            direccion=direccion,
            telefono=telefono,
            atencion=atencion,
            validez=validez,
            plazo_entrega=plazo_entrega,
            forma_pago=forma_pago,
            observaciones=observaciones
        )

        db.session.add(cotizacion)
        db.session.commit()

        # =========================
        # DETALLES
        # =========================
        for p in productos_seleccionados:

            producto = None

            if p.get("id"):
                producto = Producto.query.get(p["id"])

            if producto:
                detalle = DetalleCotizacion(
                    cotizacion_id=cotizacion.id,
                    producto_id=producto.id,
                    descripcion=p["nombre"],
                    cantidad=p["cantidad"],
                    precio=p["precio"],
                    total=p["precio"] * p["cantidad"],
                    imagen=producto.imagen,
                    detalle=producto.detalle
                )
            else:
                detalle = DetalleCotizacion(
                    cotizacion_id=cotizacion.id,
                    producto_id=None,
                    descripcion=p["nombre"],
                    cantidad=p["cantidad"],
                    precio=p["precio"],
                    total=p["precio"] * p["cantidad"],
                    imagen=None,
                    detalle=p.get("detalle")
                )

            db.session.add(detalle)

        db.session.commit()

        return redirect(url_for("cotizaciones"))

    # =========================
    # GET
    # =========================
    productos = Producto.query.all()
    return render_template("nueva_cotizacion.html", productos=productos) 

# ---------------- VER COTIZACION ----------------
@app.route("/ver_cotizacion/<int:cotizacion_id>")
def ver_cotizacion(cotizacion_id):
    cotizacion = db.session.get(Cotizacion, cotizacion_id)
    if not cotizacion:
        return redirect(url_for("cotizaciones"))

    total_literal = numero_a_literal(float(cotizacion.total))

    cliente_nombre = cotizacion.cliente.nombre if cotizacion.cliente else "Cliente no registrado"
    cliente_nit = cotizacion.cliente.nit_ci if cotizacion.cliente else ""

    return render_template(
        "cotizacion_pdf.html",
        pdf_mode=False,

        empresa=SinConfig.RAZON_SOCIAL,
        numero=cotizacion.numero,
        fecha=cotizacion.fecha.strftime("%d/%m/%Y "),

        cliente=cliente_nombre,
        nit_ci=cliente_nit,

        # 🔥 DATOS REALES (FIX)
        email=cotizacion.email,
        celular=cotizacion.celular,
        telefono=cotizacion.telefono,
        direccion=cotizacion.direccion,
        atencion=cotizacion.atencion,

        validez=cotizacion.validez,
        plazo_entrega=cotizacion.plazo_entrega,
        forma_pago=cotizacion.forma_pago,
        observaciones=cotizacion.observaciones,

        detalles=cotizacion.detalles,
        subtotal=cotizacion.subtotal,
        descuento=cotizacion.descuento,
        total=cotizacion.total,
        total_literal=total_literal,

        logo_url=url_for('static', filename='logo.png')
    )

# ---------------- DESCARGAR COTIZACION PDF ----------------
@app.route("/descargar_cotizacion/<int:cotizacion_id>")
def descargar_cotizacion(cotizacion_id):
    from flask import request, url_for

    cotizacion = db.session.get(Cotizacion, cotizacion_id)
    
    if not cotizacion:
        return redirect(url_for("cotizaciones"))

    total_literal = numero_a_literal(float(cotizacion.total))

    # Logo
    logo_url = url_for(
        "static",
        filename="logo.png",
        _external=True
    )

    cliente_nombre = (
        cotizacion.cliente.nombre
        if cotizacion.cliente
        else "Cliente no registrado"
    )

    cliente_nit = (
        cotizacion.cliente.nit_ci
        if cotizacion.cliente
        else ""
    )

    # Productos con imágenes
    detalles_pdf = []

    for d in cotizacion.detalles:
        imagen_url = None

        if d.imagen:
            imagen_url = (
                request.url_root.rstrip("/")
                + "/uploads/"
                + d.imagen
            )

        detalles_pdf.append({
            "descripcion": d.descripcion,
            "detalle": d.detalle,
            "cantidad": d.cantidad,
            "precio": d.precio,
            "total": d.total,
            "imagen": d.imagen,
            "imagen_url": imagen_url
        })

    html = render_template(
        "cotizacion_pdf.html",
        empresa=SinConfig.RAZON_SOCIAL,
        numero=cotizacion.numero,
        fecha=cotizacion.fecha.strftime("%d/%m/%Y %H:%M"),
        cliente=cliente_nombre,
        nit_ci=cliente_nit,
        email=cotizacion.email,
        celular=cotizacion.celular,
        telefono=cotizacion.telefono,
        direccion=cotizacion.direccion,
        atencion=cotizacion.atencion,
        validez=cotizacion.validez,
        plazo_entrega=cotizacion.plazo_entrega,
        forma_pago=cotizacion.forma_pago,
        observaciones=cotizacion.observaciones,
        detalles=detalles_pdf,
        subtotal=cotizacion.subtotal,
        descuento=cotizacion.descuento,
        total=cotizacion.total,
        total_literal=total_literal,
        logo_url=logo_url,
        es_pdf=True
    )

    # Generar PDF
    pdf = HTML(
        string=html,
        base_url=request.url_root
    ).write_pdf()

    fecha_str = cotizacion.fecha.strftime("%Y%m%d")
    cliente_str = cliente_nombre.replace(" ", "_").upper()

    filename = (
        f"Cotizacion-REDHUALL-"
        f"{cotizacion.numero}-"
        f"{cliente_str}-"
        f"{fecha_str}.pdf"
    )

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = (
        f"attachment; filename={filename}"
    )

    return response

# ---------------- ELIMINAR COTIZACION ----------------
@app.route("/eliminar_cotizacion/<int:cotizacion_id>", methods=["POST"])
def eliminar_cotizacion(cotizacion_id):
    cotizacion = db.session.get(Cotizacion, cotizacion_id)
    if cotizacion:
        db.session.delete(cotizacion)
        db.session.commit()
    return redirect(url_for("cotizaciones"))

from flask import flash

# ---------------- FACTURAR DESDE COTIZACION ----------------
@app.route("/facturar_cotizacion/<int:cotizacion_id>")
def facturar_cotizacion(cotizacion_id):
    cotizacion = db.session.get(Cotizacion, cotizacion_id)

    if not cotizacion:
        flash("❌ Cotización no encontrada", "danger")
        return redirect(url_for("cotizaciones"))

    # 🔢 Número de factura
    numero_factura = (db.session.query(func.max(Factura.numero)).scalar() or 0) + 1

    # 🧾 Crear factura
    factura = Factura(
        numero=numero_factura,
        fecha=datetime.now(),
        cliente_id=cotizacion.cliente_id,
        total=cotizacion.total
    )

    db.session.add(factura)
    db.session.commit()

    # 📦 Crear detalles de factura
    for d in cotizacion.detalles:
        if not d.producto_id:
            flash("⚠️ Error: esta cotización es antigua y no tiene productos válidos", "warning")
            return redirect(url_for("cotizaciones"))

        detalle = DetalleFactura(
            factura_id=factura.id,
            producto_id=d.producto_id,
            cantidad=d.cantidad,
            precio_unitario=d.precio,
            subtotal=d.total
        )
        db.session.add(detalle)

    db.session.commit()

    # ✅ MENSAJE PRO
    flash(f"✅ Factura N° {factura.numero} generada correctamente", "success")

    # 🔥 Redirigir a ver factura directamente
    return redirect(url_for("ver_factura", factura_id=factura.id))
# ---------------- ELIMINAR FACTURA ----------------
@app.route("/eliminar_factura/<int:factura_id>", methods=["POST"])
def eliminar_factura(factura_id):
    factura = db.session.get(Factura, factura_id)

    if not factura:
        flash("❌ Factura no encontrada", "danger")
        return redirect(url_for("facturas"))

    db.session.delete(factura)
    db.session.commit()

    flash(f"🗑️ Factura N° {factura.numero} eliminada correctamente", "success")
    return redirect(url_for("facturas"))
#-------------------------------------
from flask import send_from_directory, abort
import os

@app.route('/uploads/<path:filename>')
def uploaded_files(filename):
    uploads_path = os.path.join(app.root_path, 'static', 'uploads', 'productos')

    file_path = os.path.join(uploads_path, filename)

    if not os.path.isfile(file_path):
        abort(404)  # más correcto que devolver texto

    return send_from_directory(uploads_path, filename)
# ---------------- MAIN ----------------
if __name__ == "__main__":
    with app.app_context():   
        db.create_all()

        if not Usuario.query.first():
            admin = Usuario(username="Nestor", rol="admin")
            admin.set_password("1234")

            vendedor = Usuario(username="vendedor", rol="vendedor")
            vendedor.set_password("1234")

            db.session.add(admin)
            db.session.add(vendedor)
            db.session.commit()

    print("Servidor Flask corriendo en http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
    