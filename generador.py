"""
Logica de generacion de la hoja membretada.

Toma los datos (fecha, producto, precio, cliente) y los "estampa" encima
del PDF membretado original (plantillas/membrete.pdf), de modo que el estilo
quede identico al molde. Si no existe la plantilla, genera una hoja basica
de respaldo para que el programa funcione igual.

Este modulo NO depende de la interfaz grafica, asi se puede probar solo.
"""

import io
import json
import os
import re
from datetime import date

from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:  # nombre antiguo de la libreria
    from PyPDF2 import PdfReader, PdfWriter


RAIZ = os.path.dirname(os.path.abspath(__file__))


def cargar_config(ruta=None):
    """Lee config.json y lo devuelve como diccionario."""
    if ruta is None:
        ruta = os.path.join(RAIZ, "config.json")
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def _tamano_hoja(nombre):
    return LETTER if str(nombre).upper() == "LETTER" else A4


def _fuente_nombre(base, negrita):
    """Devuelve el nombre de la fuente de reportlab segun si es negrita."""
    if base == "Helvetica":
        return "Helvetica-Bold" if negrita else "Helvetica"
    if base == "Times-Roman":
        return "Times-Bold" if negrita else "Times-Roman"
    if base == "Courier":
        return "Courier-Bold" if negrita else "Courier"
    # por defecto
    return "Helvetica-Bold" if negrita else "Helvetica"


def formatear_precio(valor, simbolo="$"):
    """
    Formatea el precio de forma amigable.
    - Si ya viene con texto/simbolos, lo deja como esta (solo agrega simbolo si falta).
    - Si es un numero, lo formatea con separador de miles (estilo es-AR: 1.234,56).
    """
    if valor is None:
        return ""
    texto = str(valor).strip()
    if texto == "":
        return ""

    # Intentar interpretar como numero
    limpio = texto.replace(simbolo, "").strip()
    # quitar separadores para detectar si es numero "puro"
    candidato = limpio.replace(".", "").replace(",", ".").replace(" ", "")
    try:
        numero = float(candidato)
    except ValueError:
        # No es un numero limpio: lo dejamos tal cual lo escribio el usuario
        return texto if simbolo in texto else f"{simbolo} {texto}"

    # Formato es-AR: miles con punto, decimales con coma
    entero = int(numero)
    decimales = round(numero - entero, 2)
    entero_fmt = f"{entero:,}".replace(",", ".")
    if decimales > 0:
        dec_str = f"{decimales:.2f}".split(".")[1]
        return f"{simbolo} {entero_fmt},{dec_str}"
    return f"{simbolo} {entero_fmt}"


def _nombre_archivo_seguro(texto):
    """Convierte un texto en un nombre de archivo valido."""
    texto = texto.strip() or "hoja"
    texto = re.sub(r"[^\w\s.-]", "", texto, flags=re.UNICODE)
    texto = re.sub(r"\s+", "_", texto)
    return texto[:60]


def _dibujar_texto(c, campo_cfg, texto, alto_pagina, fuente_base, color):
    """Dibuja un texto en el canvas segun la configuracion del campo."""
    if texto is None or str(texto).strip() == "":
        return
    etiqueta = campo_cfg.get("etiqueta", "")
    contenido = f"{etiqueta}{texto}"
    tamano = campo_cfg.get("tamano", 12)
    negrita = campo_cfg.get("negrita", False)
    alineacion = campo_cfg.get("alineacion", "izquierda")

    x = campo_cfg["x"] * mm
    # y viene desde arriba -> convertir a coordenada de reportlab (desde abajo)
    y = alto_pagina - (campo_cfg["y"] * mm)

    c.setFont(_fuente_nombre(fuente_base, negrita), tamano)
    c.setFillColor(color)

    if alineacion == "derecha":
        c.drawRightString(x, y, contenido)
    elif alineacion in ("centro", "centrado", "center"):
        c.drawCentredString(x, y, contenido)
    else:
        c.drawString(x, y, contenido)


def _crear_overlay(datos, config, ancho, alto):
    """Crea un PDF en memoria con solo los datos variables (capa transparente)."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(ancho, alto))

    color = HexColor(config.get("fuente", {}).get("color", "#222222"))
    fuente_base = config.get("fuente", {}).get("nombre", "Helvetica")
    campos = config.get("campos", {})

    mapa = {
        "fecha": datos.get("fecha", ""),
        "nombre_cliente": datos.get("nombre_cliente", ""),
        "producto": datos.get("producto", ""),
        "precio": datos.get("precio", ""),
    }

    for clave, valor in mapa.items():
        if clave in campos:
            _dibujar_texto(c, campos[clave], valor, alto, fuente_base, color)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


def _dibujar_membrete_basico(c, ancho, alto):
    """Membrete de respaldo cuando todavia no hay PDF molde."""
    c.setFillColor(HexColor("#1f3a5f"))
    c.rect(0, alto - 28 * mm, ancho, 28 * mm, fill=1, stroke=0)
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 22)
    c.drawString(25 * mm, alto - 18 * mm, "MI EMPRESA S.A.")
    c.setFont("Helvetica", 9)
    c.drawString(25 * mm, alto - 24 * mm, "Direccion 123 - Tel: 000-0000 - mail@empresa.com")
    # pie
    c.setFillColor(HexColor("#1f3a5f"))
    c.rect(0, 0, ancho, 12 * mm, fill=1, stroke=0)
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica", 8)
    c.drawCentredString(ancho / 2, 4.5 * mm, "(membrete de ejemplo - reemplazar por plantillas/membrete.pdf)")


def generar(datos, config=None, ruta_salida=None):
    """
    Genera la hoja membretada en PDF.

    datos: dict con claves fecha, nombre_cliente, producto, precio.
    Devuelve la ruta del PDF generado.
    """
    if config is None:
        config = cargar_config()

    simbolo = config.get("simbolo_moneda", "$")
    datos = dict(datos)
    datos["precio"] = formatear_precio(datos.get("precio", ""), simbolo)
    if not datos.get("fecha"):
        datos["fecha"] = date.today().strftime("%d/%m/%Y")

    plantilla_rel = config.get("plantilla_pdf", "plantillas/membrete.pdf")
    plantilla_path = os.path.join(RAIZ, plantilla_rel)
    usar_plantilla = os.path.isfile(plantilla_path)

    if usar_plantilla:
        lector = PdfReader(plantilla_path)
        pagina_base = lector.pages[0]
        ancho = float(pagina_base.mediabox.width)
        alto = float(pagina_base.mediabox.height)
    else:
        ancho, alto = _tamano_hoja(config.get("tamano_hoja", "A4"))

    overlay_buffer = _crear_overlay(datos, config, ancho, alto)

    escritor = PdfWriter()

    if usar_plantilla:
        overlay_pdf = PdfReader(overlay_buffer)
        pagina = lector.pages[0]
        pagina.merge_page(overlay_pdf.pages[0])
        escritor.add_page(pagina)
    else:
        # Generar pagina completa (membrete basico + datos) desde cero
        base_buffer = io.BytesIO()
        c = canvas.Canvas(base_buffer, pagesize=(ancho, alto))
        _dibujar_membrete_basico(c, ancho, alto)
        c.showPage()
        c.save()
        base_buffer.seek(0)
        base_pdf = PdfReader(base_buffer)
        overlay_pdf = PdfReader(overlay_buffer)
        pagina = base_pdf.pages[0]
        pagina.merge_page(overlay_pdf.pages[0])
        escritor.add_page(pagina)

    # Definir ruta de salida
    if ruta_salida is None:
        carpeta = os.path.join(RAIZ, config.get("carpeta_salida", "salida"))
        os.makedirs(carpeta, exist_ok=True)
        cliente = _nombre_archivo_seguro(datos.get("nombre_cliente", "hoja"))
        hoy = date.today().strftime("%Y%m%d")
        ruta_salida = os.path.join(carpeta, f"hoja_{cliente}_{hoy}.pdf")
        # evitar pisar archivos
        contador = 1
        base, ext = os.path.splitext(ruta_salida)
        while os.path.exists(ruta_salida):
            ruta_salida = f"{base}_{contador}{ext}"
            contador += 1

    with open(ruta_salida, "wb") as f:
        escritor.write(f)

    return ruta_salida


if __name__ == "__main__":
    # Prueba rapida desde la terminal
    ruta = generar({
        "fecha": "",
        "nombre_cliente": "Juan Perez",
        "producto": "Bolsa de cemento 50kg",
        "precio": "12500.5",
    })
    print(f"PDF generado en: {ruta}")
