import datetime
import uuid
import xml.etree.ElementTree as ET
from xml.dom import minidom

def generar_xml_factura(factura_data):
    """
    Genera un XML de la factura utilizando xml.etree.ElementTree.
    """
    raiz = ET.Element("facturaElectronica")

    cabecera = ET.SubElement(raiz, "cabecera")
    ET.SubElement(cabecera, "nitEmisor").text = str(factura_data['nit'])
    ET.SubElement(cabecera, "razonSocialEmisor").text = factura_data['razon_social']
    ET.SubElement(cabecera, "numeroFactura").text = str(factura_data['numero'])
    ET.SubElement(cabecera, "fechaEmision").text = factura_data.get("fecha", datetime.datetime.now().isoformat())

    detalle = ET.SubElement(raiz, "detalle")
    for item in factura_data["items"]:
        producto = ET.SubElement(detalle, "producto")
        ET.SubElement(producto, "descripcion").text = item['descripcion']
        ET.SubElement(producto, "cantidad").text = str(item['cantidad'])
        ET.SubElement(producto, "precioUnitario").text = str(item['precio'])
        ET.SubElement(producto, "subtotal").text = str(item['subtotal'])

    totales = ET.SubElement(raiz, "totales")
    ET.SubElement(totales, "montoTotal").text = str(factura_data['total'])
    ET.SubElement(totales, "moneda").text = "BOB"

    # Convertir el XML a un string con formato
    xml_string = ET.tostring(raiz, encoding='utf8', method='xml').decode('utf8')
    dom = minidom.parseString(xml_string)
    pretty_xml = dom.toprettyxml(indent="  ")

    return pretty_xml

def enviar_factura(factura_data):
    """
    Simula el envío al SIN y devuelve un CUF ficticio.
    """
    cuf = uuid.uuid4().hex.upper()  # CUF simulado más realista
    return {
        "estado": "VALIDADA",
        "cuf": cuf,
        "fecha": datetime.datetime.now().isoformat()
    }