# Generador de Hojas Membretadas — SKIN LEATHER

Genera hojas membretadas en PDF de forma automática, con el estilo del membrete
de **Skin Leather (Taller de Cuero S.A.S.)**. Cargás el **cliente**, la **fecha**
y una lista de **productos con su precio**, y obtenés el PDF listo, con el total
calculado.

Hay dos formas de usarlo:

## 1) Página web (para el celular) — recomendado

Es una página que se abre con un link, ideal para usar desde el celular. Tu papá
(o cualquiera) abre el link, completa el cuadro y descarga el PDF. No instala nada.

- Archivo: `index.html`
- Hosting gratis con **GitHub Pages** (ya hay un workflow que lo publica solo).
- Para activarlo una sola vez: en GitHub → **Settings → Pages → Source: "GitHub Actions"**.
- Link: `https://fcade22.github.io/fcade22/`

Funciona entero en el navegador (no necesita servidor ni claves de API) y arma el
PDF usando `plantillas/membrete.pdf` como fondo.

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
- `tabla`: posición de la lista de productos, alto de cada fila, encabezados
  ("PRODUCTO" / "PRECIO") y si muestra el total.

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
