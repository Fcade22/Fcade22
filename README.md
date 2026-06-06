# Generador de Hojas Membretadas — SKIN LEATHER

Genera hojas membretadas en PDF de forma automática, con el estilo del membrete
de **Skin Leather (Taller de Cuero S.A.S.)**. Cargás el **cliente**, la **fecha**
y una lista de **productos con su precio**, y obtenés el PDF listo, con el total
calculado.

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

Funciona entero en el navegador (no necesita servidor ni claves de API) y arma el
PDF usando `plantillas/membrete.pdf` como fondo. La librería de PDF
(`pdf-lib.min.js`) está incluida en el proyecto, así no depende de internet.

## 2) App de escritorio (para la computadora)

Una ventana que se abre con doble clic.

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

Todo lo visual del PDF se controla en `config.json` (lo comparten la web y la app):

- `fecha` / `cliente`: posición (en milímetros desde la esquina superior izquierda),
  tamaño, negrita, alineación y etiqueta.
- `tabla`: posición de las columnas (producto, cantidad, precio unitario,
  importe), alto de cada fila, encabezados, si muestra el total y la `nota`
  al pie (ej: "LOS PRECIOS NO INCLUYEN EL IVA").

Cada renglón calcula el importe (cantidad × precio unitario) y el total los suma.

El membrete original es `plantillas/membrete.pdf`. Si lo cambiás, puede que haya
que reajustar las coordenadas.

## Archivos

- `index.html` — la página web (formulario + generación del PDF en el navegador).
- `app.py` — la app de escritorio.
- `generador.py` — la lógica que arma el PDF (la usa la app de escritorio).
- `config.json` — posiciones, fuentes, colores y encabezados.
- `plantillas/membrete.pdf` — el molde membretado.
- `salida/` — donde la app de escritorio guarda los PDF.
- `.github/workflows/deploy-pages.yml` — publica la web en GitHub Pages.
