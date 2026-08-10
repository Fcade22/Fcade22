# Documentos — SKIN LEATHER

Genera en PDF los documentos de **Skin Leather (Taller de Cuero S.A.S.)** sobre el
membrete de la casa. Son dos, y se eligen con las pestañas de arriba:

- **Presupuesto** — cliente, fecha, la lista de **productos con cantidad y precio
  unitario** y la **forma de pago**. Cada producto se lleva el ancho entero de la
  hoja para su descripción (y sigue abajo si es larga), con la cantidad y el precio
  unitario debajo. Calcula el importe de cada renglón y el total.
- **Recibo** — cliente, fecha, **recibimos de**, **la suma de pesos** y **en concepto
  de**. El importe se escribe en números y la app lo pasa solo a letras (se puede
  corregir a mano; si después cambia el número, se reescribe, porque en un recibo
  las letras y los números no pueden decir cosas distintas).

Los dos llevan **numeración correlativa** y salen firmados al pie por
**Gabriel Levene · Administrador**.

### La numeración

Cada documento tiene su propia serie (los presupuestos por un lado, los recibos por
otro), arranca en `0001` y **avanza sola** recién cuando el PDF salió bien, así un
error no consume un número. El campo se puede editar: si ya venías numerando a mano,
escribí el número que toca y desde ahí sigue solo.

**El contador vive en el celular** (en el almacenamiento del navegador). Eso quiere
decir que si se reinstala la app, se borran los datos del navegador o se pasa a otro
teléfono, arranca de nuevo en `0001` y hay que reponer el número a mano. Tampoco se
sincroniza entre dos dispositivos: si se usa en el celular y en la compu, cada uno
lleva su cuenta.

Hay dos formas de usarlo:

## 1) App web instalable (para el celular) — recomendado

Es una página que se abre con un link y se puede **instalar como app** en el
celular (ícono en la pantalla de inicio). Funciona **sin internet** una vez
abierta la primera vez. Ideal para pasársela a otra persona: solo mandás el link.

- Link: `https://fcade22.github.io/Fcade22/`
- Hosting gratis con **GitHub Pages** (el workflow la publica sola en cada cambio).

**Instalarla como app:**
- **Android (Chrome):** abrir el link → menú (⋮) → "Agregar a pantalla principal"
  / "Instalar app".
- **iPhone (Safari):** abrir el link → botón Compartir → "Agregar a inicio".

Si ya la tenías instalada, **se actualiza sola**: el service worker busca la
versión nueva cada vez que la abrís.

Funciona entero en el navegador (no necesita servidor ni claves de API) y arma el
PDF usando `plantillas/membrete.pdf` como fondo. La librería de PDF
(`pdf-lib.min.js`) está incluida en el proyecto, así no depende de internet.

## 2) App de escritorio (para la computadora)

Una ventana que se abre con doble clic. **Ojo: quedó atrás.** Solo hace
presupuestos, con el layout viejo de cuatro columnas, y no sabe nada de la
numeración, la forma de pago ni la firma. Todo eso vive únicamente en la app web.

**Requisitos:** Python 3.9+ instalado.

**Instalación (una vez):**
```
pip install -r requirements.txt
```

**Uso:**
```
python app.py
```
Cargás cliente, fecha y los productos (con el botón "+ Agregar producto"),
apretás **Generar PDF** y el archivo queda en la carpeta `salida/`.

## Ajustar el diseño

Todo lo visual del PDF se controla en `config.json`. Las coordenadas van en
**milímetros desde la esquina superior izquierda** de la hoja A4 (210 × 297 mm).
El encabezado del membrete ocupa hasta ~43 mm y el pie arranca a ~240 mm: todo lo
que se dibuje tiene que caer entre esos dos límites.

- `fecha` / `cliente` / `numero`: los comparten los dos documentos (posición,
  tamaño, negrita, alineación y etiqueta). En `numero`, `digitos` es con cuántos
  ceros adelante se escribe (4 → `0001`).
- `tabla`: el presupuesto — margen izquierdo y derecho, alto de renglón, separación
  entre productos, encabezados, si muestra el total y la `nota` al pie (ej: "LOS
  PRECIOS NO INCLUYEN EL IVA").
- `forma_pago`: el casillero al pie del presupuesto — etiqueta, altura y tamaños.
- `recibo`: el recibo — el título y la altura de cada una de las tres líneas
  ("recibimos de" / "la suma de pesos" / "en concepto de"). Esas alturas son el
  punto de partida: si un valor ocupa más de un renglón, lo que sigue baja solo.
- `firma`: el bloque de firma que va al pie de los dos documentos — nombre, cargo,
  posición y tamaños.

El membrete original es `plantillas/membrete.pdf`. Si lo cambiás, puede que haya
que reajustar las coordenadas.

## Archivos

- `index.html` — la app web entera (los dos formularios + la generación del PDF).
- `app.py` — la app de escritorio (solo presupuestos).
- `generador.py` — la lógica que arma el PDF (la usa la app de escritorio).
- `config.json` — posiciones, fuentes, colores, encabezados y firma.
- `plantillas/membrete.pdf` — el molde membretado.
- `salida/` — donde la app de escritorio guarda los PDF.
- `sw.js` / `manifest.json` — lo que la hace instalable y offline.
- `.github/workflows/deploy-pages.yml` — publica la web en GitHub Pages.
