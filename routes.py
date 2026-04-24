from flask import render_template, request, redirect, url_for, flash, make_response, current_app, session
from app import app, db
from models import Factura, Cliente, DetalleFactura, Producto
from sin_api import enviar_factura, generar_xml_factura
from config_sin import SinConfig
import datetime
import pdfkit  # asegúrate de instalarlo con: python -m pip install pdfkit
import os
from sqlalchemy import exc

@app.route("/pos")
def pos():
    return render_template("pos.html")

@app.route("/facturas")
def facturas():
    """Lista todas las facturas registradas."""
    facturas = Factura.query.all()
    return render_template(
        "facturas.html",
        facturas=facturas,
        empresa=SinConfig.RAZON_SOCIAL,
        nit=SinConfig.NIT,
    )

@app.route("/confirmar_factura", methods=["POST"])
def confirmar_factura():
    """Confirma la factura, genera el XML, la envía al SIN y guarda los datos."""
    nombre_cliente = request.form["nombre"]
    nit_ci_cliente = request.form["nit_ci"]

    # Obtener los datos del carrito de la sesión
    carrito = session.get("carrito", [])
    if not carrito:
        flash("El carrito está vacío.", "error")
        return redirect(url_for("pos"))

    # Calcular el total real del carrito
    total = sum(item["subtotal"] for item in carrito)

    try:
        # Crear el cliente si no existe
        cliente = Cliente.query.filter_by(nit_ci=nit_ci_cliente).first()
        if not cliente:
            cliente = Cliente(nombre=nombre_cliente, nit_ci=nit_ci_cliente)
            db.session.add(cliente)
            db.session.commit()

        # Crear la factura
        numero_factura = Factura.query.count() + 1
        factura_data = {
            "nit": SinConfig.NIT,
            "razon_social": SinConfig.RAZON_SOCIAL,
            "numero": numero_factura,
            "fecha": datetime.datetime.now().isoformat(),
            "items": [
                {
                    "descripcion": item["nombre"],
                    "cantidad": item["cantidad"],
                    "precio": item["precio"],
                    "subtotal": item["subtotal"],
                }
                for item in carrito
            ],
            "total": total,
        }

        # Generar el XML y enviar la factura al SIN
        xml = generar_xml_factura(factura_data)
        respuesta = enviar_factura(factura_data)

        # Crear la factura en la base de datos
        nueva_factura = Factura(
            numero=numero_factura,
            cliente_id=cliente.id,
            total=total,
            cuf=respuesta["cuf"],
        )
        db.session.add(nueva_factura)

        # Crear los detalles de la factura
        for item in carrito:
            producto = Producto.query.get(item["producto_id"])
            if producto:
                detalle = DetalleFactura(
                    factura_id=nueva_factura.id,
                    producto_id=producto.id,
                    cantidad=item["cantidad"],
                    precio_unitario=item["precio"],
                    subtotal=item["subtotal"],
                )
                db.session.add(detalle)

        # Commit único para eficiencia
        db.session.commit()

        # Limpiar el carrito
        session["carrito"] = []

        flash(f"Factura generada con CUF {respuesta['cuf']}", "success")
        return redirect(url_for("facturas"))

    except exc.SQLAlchemyError as e:
        db.session.rollback()
        flash(f"Error al confirmar la factura: {str(e)}", "error")
        return redirect(url_for("pos"))
    except Exception as e:
        flash(f"Error inesperado: {str(e)}", "error")
        return redirect(url_for("pos"))

# 👉 Ruta para ver la factura oficial (HTML)
@app.route("/factura/<int:factura_id>")
def factura(factura_id):
    """Muestra la factura en formato HTML."""
    factura = Factura.query.get_or_404(factura_id)
    detalles = DetalleFactura.query.filter_by(factura_id=factura.id).all()
    return render_template(
        "factura.html",
        empresa=SinConfig.RAZON_SOCIAL,
        nit=SinConfig.NIT,
        numero=factura.numero,
        fecha=factura.fecha.strftime("%d/%m/%Y %H:%M"),
        cliente=factura.cliente.nombre,
        nit_ci=factura.cliente.nit_ci,
        detalles=detalles,
        total=factura.total,
        cuf=factura.cuf,
    )

# 👉 Ruta para descargar la factura en PDF
@app.route("/descargar_factura/<int:factura_id>")
def descargar_factura(factura_id):
    """Genera y descarga la factura en formato PDF."""
    factura = Factura.query.get_or_404(factura_id)
    detalles = DetalleFactura.query.filter_by(factura_id=factura.id).all()
    rendered = render_template(
        "factura.html",
        empresa=SinConfig.RAZON_SOCIAL,
        nit=SinConfig.NIT,
        numero=factura.numero,
        fecha=factura.fecha.strftime("%d/%m/%Y %H:%M"),
        cliente=factura.cliente.nombre,
        nit_ci=factura.cliente.nit_ci,
        detalles=detalles,
        total=factura.total,
        cuf=factura.cuf,
    )

    # Configurar las opciones de PDFKit
    config = pdfkit.configuration(
        wkhtmltopdf=os.environ.get("WKHTMLTOPDF_PATH", "/usr/bin/wkhtmltopdf")
    )
    options = {
        "margin-top": "10mm",
        "margin-right": "10mm",
        "margin-bottom": "10mm",
        "margin-left": "10mm",
        "encoding": "UTF-8",
    }

    # Generar PDF desde HTML
    try:
        pdf = pdfkit.from_string(rendered, False, options=options, configuration=config)
    except Exception as e:
        current_app.logger.error(f"Error al generar el PDF: {e}")
        flash("Error al generar el PDF.", "error")
        return redirect(url_for("factura", factura_id=factura_id))

    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"attachment; filename=factura_{factura.numero}.pdf"
    return response