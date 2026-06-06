"""
Logica de generacion de la hoja membretada.

Toma los datos (fecha, cliente y una lista de productos con su precio) y los
"estampa" encima del PDF membretado original (plantillas/membrete.pdf), de modo
que el estilo quede identico al molde. Si no existe la plantilla, genera una
hoja basica de respaldo para que el programa funcione igual.

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
    if base == "Times-Roman":
        return "Times-Bold" if negrita else "Times-Roman"
    if base == "Courier":
        return "Courier-Bold" if negrita else "Courier"
    return "Helvetica-Bold" if negrita else "Helvetica"


def parse_numero(valor):
    """Intenta interpretar un texto como numero. Devuelve float o None."""
    if valor is None:
        return None
    texto = str(valor).strip()
    if texto == "":
        return None
    limpio = re.sub(r"[^\d,.\-]", "", texto)
    # formato es-AR: punto = miles, coma = decimal
    candidato = limpio.replace(".", "").replace(",", ".")
    try:
        return float(candidato)
    except ValueError:
        return None


def formatear_precio(valor, simbolo="$"):
    """Formatea un precio de forma amigable (estilo es-AR: 1.234,56)."""
    numero = parse_numero(valor)
    if numero is None:
        texto = str(valor).strip()
        if texto == "":
            return ""
        return texto if simbolo in texto else f"{simbolo} {texto}"
    return _formatear_numero(numero, simbolo)


def _formatear_numero(numero, simbolo):
    entero = int(numero)
    decimales = round(abs(numero) - abs(entero), 2)
    entero_fmt = f"{entero:,}".replace(",", ".")
    if decimales > 0:
        dec_str = f"{decimales:.2f}".split(".")[1]
        return f"{simbolo} {entero_fmt},{dec_str}"
    return f"{simbolo} {entero_fmt}"


def _nombre_archivo_seguro(texto):
    """Convierte un texto en un nombre de archivo valido."""
    texto = (texto or "hoja").strip() or "hoja"
    texto = re.sub(r"[^\w\s.-]", "", texto, flags=re.UNICODE)
    texto = re.sub(r"\s+", "_", texto)
    return texto[:60] or "hoja"


def _normalizar_productos(datos):
    """Acepta lista de productos o un unico producto/precio (compatibilidad)."""
    productos = datos.get("productos")
    if productos:
        salida = []
        for p in productos:
            nombre = str(p.get("producto", "")).strip()
            precio = p.get("precio", "")
            if nombre or str(precio).strip():
                salida.append({"producto": nombre, "precio": precio})
        return salida
    # compatibilidad con el formato viejo (un solo producto)
    if datos.get("producto"):
        return [{"producto": datos["producto"], "precio": datos.get("precio", "")}]
    return []


def _texto(c, x_mm, y_mm_desde_arriba, alto_pagina, texto, tamano,
           fuente_base, negrita, color, alineacion="izquierda"):
    if texto is None or str(texto) == "":
        return
    x = x_mm * mm
    y = alto_pagina - (y_mm_desde_arriba * mm)
    c.setFont(_fuente_nombre(fuente_base, negrita), tamano)
    c.setFillColor(color)
    if alineacion == "derecha":
        c.drawRightString(x, y, str(texto))
    elif alineacion in ("centro", "centrado", "center"):
        c.drawCentredString(x, y, str(texto))
    else:
        c.drawString(x, y, str(texto))


def _linea(c, x1_mm, x2_mm, y_mm_desde_arriba, alto_pagina, color, grosor=0.6):
    c.setStrokeColor(color)
    c.setLineWidth(grosor)
    y = alto_pagina - (y_mm_desde_arriba * mm)
    c.line(x1_mm * mm, y, x2_mm * mm, y)


def _dibujar_contenido(c, datos, config, ancho, alto):
    """Dibuja fecha, cliente y la tabla de productos sobre el canvas."""
    color = HexColor(config.get("fuente", {}).get("color", "#3b2a1d"))
    fuente_base = config.get("fuente", {}).get("nombre", "Helvetica")
    simbolo = config.get("simbolo_moneda", "$")

    # Fecha
    f = config.get("fecha", {})
    if f:
        fecha_txt = f.get("etiqueta", "") + str(datos.get("fecha", ""))
        _texto(c, f.get("x", 185), f.get("y", 56), alto, fecha_txt,
               f.get("tamano", 11), fuente_base, f.get("negrita", False),
               color, f.get("alineacion", "derecha"))

    # Cliente
    cl = config.get("cliente", {})
    if cl and datos.get("nombre_cliente"):
        cli_txt = cl.get("etiqueta", "") + str(datos["nombre_cliente"])
        _texto(c, cl.get("x", 25), cl.get("y", 60), alto, cli_txt,
               cl.get("tamano", 13), fuente_base, cl.get("negrita", True),
               color, cl.get("alineacion", "izquierda"))

    # Tabla de productos
    t = config.get("tabla", {})
    productos = _normalizar_productos(datos)
    x_prod = t.get("x_producto", 25)
    x_precio = t.get("x_precio", 185)
    y = t.get("y_encabezado", 80)
    alto_fila = t.get("alto_fila", 9)
    tam = t.get("tamano", 11)
    tam_enc = t.get("tamano_encabezado", tam)

    # Encabezado de la tabla
    _texto(c, x_prod, y, alto, t.get("encabezado_producto", "PRODUCTO"),
           tam_enc, fuente_base, True, color, "izquierda")
    _texto(c, x_precio, y, alto, t.get("encabezado_precio", "PRECIO"),
           tam_enc, fuente_base, True, color, "derecha")
    _linea(c, x_prod, x_precio, y + 2, alto, color, 0.8)

    # Filas
    total = 0.0
    hay_total = False
    y_fila = y + alto_fila
    for p in productos:
        _texto(c, x_prod, y_fila, alto, p["producto"], tam,
               fuente_base, False, color, "izquierda")
        precio_fmt = formatear_precio(p["precio"], simbolo)
        _texto(c, x_precio, y_fila, alto, precio_fmt, tam,
               fuente_base, False, color, "derecha")
        n = parse_numero(p["precio"])
        if n is not None:
            total += n
            hay_total = True
        y_fila += alto_fila

    # Total
    if t.get("mostrar_total", True) and hay_total and productos:
        _linea(c, x_prod, x_precio, y_fila - alto_fila + 2.5, alto, color, 0.8)
        y_total = y_fila + 1
        _texto(c, x_prod, y_total, alto, t.get("etiqueta_total", "TOTAL"),
               tam, fuente_base, True, color, "izquierda")
        _texto(c, x_precio, y_total, alto, _formatear_numero(total, simbolo),
               tam, fuente_base, True, color, "derecha")


def _dibujar_membrete_basico(c, ancho, alto):
    """Membrete de respaldo cuando todavia no hay PDF molde."""
    c.setFillColor(HexColor("#5a4231"))
    c.rect(0, alto - 28 * mm, ancho, 28 * mm, fill=1, stroke=0)
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 22)
    c.drawString(25 * mm, alto - 18 * mm, "MI EMPRESA")
    c.setFont("Helvetica", 9)
    c.drawString(25 * mm, alto - 24 * mm, "Direccion 123 - Tel: 000-0000")
    c.setFillColor(HexColor("#5a4231"))
    c.rect(0, 0, ancho, 12 * mm, fill=1, stroke=0)
    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica", 8)
    c.drawCentredString(ancho / 2, 4.5 * mm,
                        "(membrete de ejemplo - reemplazar por plantillas/membrete.pdf)")


def generar(datos, config=None, ruta_salida=None):
    """
    Genera la hoja membretada en PDF.

    datos: dict con claves:
      - fecha (str)
      - nombre_cliente (str)
      - productos: lista de {"producto": str, "precio": str}
    Devuelve la ruta del PDF generado.
    """
    if config is None:
        config = cargar_config()

    datos = dict(datos)
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

    # Crear capa con el contenido
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(ancho, alto))
    if not usar_plantilla:
        _dibujar_membrete_basico(c, ancho, alto)
    _dibujar_contenido(c, datos, config, ancho, alto)
    c.showPage()
    c.save()
    buffer.seek(0)

    escritor = PdfWriter()
    overlay_pdf = PdfReader(buffer)
    if usar_plantilla:
        pagina = lector.pages[0]
        pagina.merge_page(overlay_pdf.pages[0])
        escritor.add_page(pagina)
    else:
        escritor.add_page(overlay_pdf.pages[0])

    if ruta_salida is None:
        carpeta = os.path.join(RAIZ, config.get("carpeta_salida", "salida"))
        os.makedirs(carpeta, exist_ok=True)
        cliente = _nombre_archivo_seguro(datos.get("nombre_cliente", "hoja"))
        hoy = date.today().strftime("%Y%m%d")
        ruta_salida = os.path.join(carpeta, f"hoja_{cliente}_{hoy}.pdf")
        base, ext = os.path.splitext(ruta_salida)
        contador = 1
        while os.path.exists(ruta_salida):
            ruta_salida = f"{base}_{contador}{ext}"
            contador += 1

    with open(ruta_salida, "wb") as f:
        escritor.write(f)

    return ruta_salida


if __name__ == "__main__":
    ruta = generar({
        "fecha": "",
        "nombre_cliente": "Juan Perez",
        "productos": [
            {"producto": "Billetera de cuero marron", "precio": "45000"},
            {"producto": "Cinturon de cuero", "precio": "18000"},
            {"producto": "Llavero artesanal", "precio": "5500"},
        ],
    })
    print(f"PDF generado en: {ruta}")
