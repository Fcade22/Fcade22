# Generador de Hojas Membretadas

Programa de escritorio que genera hojas membretadas en PDF de forma automática.
Cargás **fecha, nombre del cliente, producto y precio** en un cuadro, apretás
"Generar PDF" y obtenés la hoja con el **mismo estilo** que tu membrete original.

## Cómo funciona

El programa toma tu PDF membretado (`plantillas/membrete.pdf`) y lo usa como
**fondo**, estampando encima solamente los datos variables. Así el logo, los
colores, el encabezado y el pie quedan idénticos al molde original.

Si todavía no pusiste tu membrete, el programa genera una hoja de ejemplo para
que puedas probarlo igual.

## Requisitos

- **Python 3.9 o superior** instalado. (En Windows, descargalo de python.org y
  marcá la opción "Add Python to PATH" al instalar.)

## Instalación (una sola vez)

Abrí una terminal en esta carpeta y ejecutá:

```
pip install -r requirements.txt
```

## Cómo usarlo

1. Poné tu PDF membretado en la carpeta `plantillas/` con el nombre
   `membrete.pdf`.
2. Ejecutá el programa:
   ```
   python app.py
   ```
   (o doble clic en `app.py` si Python está asociado).
3. Completá el cuadro y apretá **Generar PDF**.
4. El PDF queda guardado en la carpeta `salida/` y se abre automáticamente.

## Ajustar dónde caen los datos

La posición de cada dato (fecha, cliente, producto, precio) se controla en el
archivo `config.json`. Las coordenadas `x` e `y` están en **milímetros** medidos
desde la **esquina superior izquierda** de la hoja:

- `x`: distancia hacia la derecha.
- `y`: distancia hacia abajo.

También se puede cambiar el tamaño de letra, la negrita, el color y las
etiquetas de cada campo. Cuando tengamos tu membrete real ajustamos estos
números para que todo caiga en el lugar exacto.

## Archivos

- `app.py` — la interfaz gráfica (el cuadro donde cargás los datos).
- `generador.py` — la lógica que arma el PDF.
- `config.json` — configuración de posiciones, fuentes y colores.
- `plantillas/membrete.pdf` — tu hoja membretada original (el molde).
- `salida/` — donde se guardan los PDF generados.
