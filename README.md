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

La tercera pestaña es el **Catálogo**: arma el catálogo de productos en PDF (el mismo
diseño del catálogo mayorista) con los precios que se elijan.

### El catálogo

- **Mayorista o minorista**: cada lista tiene sus propios precios. Mayorista dice
  "Catálogo mayorista 2026" y "Mayorista $ …"; minorista dice "Catálogo 2026" y "Precio $ …".
- **Precios cargados**: dice qué lista hay en el teléfono (la del último catálogo o "tus últimos
  precios") y tiene el botón para cargar los del último catálogo mayorista (o los de la web, en
  minorista). Si el teléfono no tiene la clave, el botón la pide.
- **No mostrar precios**: el catálogo sale con "Consultar precio mayorista" en todos los muebles
  y la intro invita a consultar por WhatsApp.
- **Subir todos los precios**: un porcentaje para toda la lista (negativo para bajar), con
  redondeo a $ 1.000 por defecto. "Deshacer el último cambio" vuelve atrás.
- **Precio por artículo**: cada mueble se puede cambiar a mano. Vacío = "a consulta".
- **Vigencia e IVA**: van en el párrafo de la intro. Por defecto la mayorista dice "sin IVA"
  (como los presupuestos) y la minorista no aclara.
- **Copiar los precios minoristas de la web**: trae los que hoy muestra skinleather.store.
- Al generar, el PDF se descarga y aparece **Compartir el PDF** (WhatsApp, mail…).

Las listas viven en el celular, como la numeración: cada cambio se guarda solo (la app pide
almacenamiento persistente para que Android no lo borre) y el próximo aumento se aplica sobre
los últimos precios cargados. No pasan de un teléfono a otro. Cada artículo lleva su miniatura
(`catalogo/miniaturas/`, las genera el mismo script del molde).

**La lista mayorista original va cifrada** (`catalogo/mayorista.enc.json`): este sitio es
público y la web esconde los precios mayoristas a propósito. La clave son cuatro palabras: se
escriben **una vez** en la app (botón "Cargar los precios del último catálogo mayorista") o se
abre el link `…/Fcade22/#clave=palabra-palabra-palabra-palabra`. Queda guardada en el teléfono y
no viaja a ningún servidor. La guarda Francisco en
`SkinLeather-ImageGen/src/catalogo/lista_mayorista.key` (fuera de este repo).

El catálogo se escribe sobre un **molde**: `catalogo/plantilla-<fecha>.pdf` es el catálogo
entero sin precios, y `catalogo/productos.json` dice qué artículos hay y dónde va cada
precio. Los dos los genera `SkinLeather-ImageGen/src/catalogo/armar_plantilla_catalogo.py`;
si se agregan muebles o cambia el diseño, se rehace el catálogo base y se corre ese script.

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

- `index.html` — la app web entera (los tres formularios + la generación de los PDF).
- `catalogo/` — molde del catálogo, lista de artículos, lista mayorista cifrada, fuentes
  DM Sans y `fontkit.min.js` (lo que necesita pdf-lib para usar esas fuentes).
- `app.py` — la app de escritorio (solo presupuestos).
- `generador.py` — la lógica que arma el PDF (la usa la app de escritorio).
- `config.json` — posiciones, fuentes, colores, encabezados y firma.
- `plantillas/membrete.pdf` — el molde membretado.
- `salida/` — donde la app de escritorio guarda los PDF.
- `sw.js` / `manifest.json` — lo que la hace instalable y offline.
- `.github/workflows/deploy-pages.yml` — publica la web en GitHub Pages.
