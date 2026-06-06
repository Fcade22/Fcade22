"""
Generador de hojas membretadas - Interfaz grafica de escritorio.

Abrir con doble clic (o ejecutar: python app.py).
Cargas cliente, fecha y varios productos con su precio, apretas "Generar PDF".
"""

import os
import sys
import webbrowser
from datetime import date

import tkinter as tk
from tkinter import ttk, messagebox

import generador


class App:
    def __init__(self, root):
        self.root = root
        root.title("Generador de Hojas Membretadas")
        root.geometry("560x560")
        root.minsize(520, 480)

        try:
            self.config = generador.cargar_config()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer config.json:\n{e}")
            self.config = {}

        cont = ttk.Frame(root, padding=22)
        cont.pack(fill="both", expand=True)

        ttk.Label(cont, text="Nueva hoja membretada",
                  font=("Helvetica", 16, "bold")).pack(anchor="w", pady=(0, 16))

        # Cliente
        ttk.Label(cont, text="Nombre del cliente").pack(anchor="w")
        self.cliente = ttk.Entry(cont, font=("Helvetica", 11))
        self.cliente.pack(fill="x", pady=(2, 12))

        # Fecha
        ttk.Label(cont, text="Fecha").pack(anchor="w")
        self.fecha = ttk.Entry(cont, font=("Helvetica", 11))
        self.fecha.insert(0, date.today().strftime("%d/%m/%Y"))
        self.fecha.pack(fill="x", pady=(2, 12))

        # Productos
        ttk.Label(cont, text="Productos · cantidad · precio unitario").pack(anchor="w")
        cabecera = ttk.Frame(cont)
        cabecera.pack(fill="x", pady=(2, 2))
        ttk.Label(cabecera, text="Producto", foreground="#777").pack(side="left")
        ttk.Label(cabecera, text="P. unit.", foreground="#777").pack(side="right", padx=(0, 40))
        ttk.Label(cabecera, text="Cant.", foreground="#777").pack(side="right", padx=(0, 70))

        self.filas_cont = ttk.Frame(cont)
        self.filas_cont.pack(fill="x")
        self.filas = []
        self._agregar_fila()

        ttk.Button(cont, text="+ Agregar producto",
                   command=self._agregar_fila).pack(anchor="w", pady=(6, 14))

        # Botones
        botones = ttk.Frame(cont)
        botones.pack(fill="x", side="bottom")
        ttk.Button(botones, text="Generar PDF",
                   command=self.generar).pack(side="left")
        self.estado = ttk.Label(botones, text="", foreground="#1f7a1f")
        self.estado.pack(side="left", padx=12)

        root.bind("<Return>", lambda e: self.generar())

    def _agregar_fila(self):
        fila = ttk.Frame(self.filas_cont)
        fila.pack(fill="x", pady=3)
        prod = ttk.Entry(fila, font=("Helvetica", 11))
        prod.pack(side="left", fill="x", expand=True)
        cantidad = ttk.Entry(fila, width=6, font=("Helvetica", 11), justify="center")
        cantidad.pack(side="left", padx=(8, 4))
        precio = ttk.Entry(fila, width=12, font=("Helvetica", 11))
        precio.pack(side="left", padx=(4, 8))
        registro = {"frame": fila, "producto": prod, "cantidad": cantidad, "precio": precio}

        def quitar():
            fila.destroy()
            self.filas.remove(registro)
            if not self.filas:
                self._agregar_fila()

        ttk.Button(fila, text="✕", width=3, command=quitar).pack(side="left")
        self.filas.append(registro)
        prod.focus_set()

    def _leer_productos(self):
        productos = []
        for f in self.filas:
            nombre = f["producto"].get().strip()
            precio = f["precio"].get().strip()
            cantidad = f["cantidad"].get().strip()
            if nombre or precio:
                productos.append({"producto": nombre, "cantidad": cantidad, "precio": precio})
        return productos

    def generar(self):
        cliente = self.cliente.get().strip()
        productos = [p for p in self._leer_productos() if p["producto"]]

        if not cliente:
            messagebox.showwarning("Falta un dato", "Ingresa el nombre del cliente.")
            return
        if not productos:
            messagebox.showwarning("Falta un dato", "Agrega al menos un producto.")
            return

        datos = {
            "fecha": self.fecha.get().strip(),
            "nombre_cliente": cliente,
            "productos": productos,
        }

        self.estado.config(text="Generando...", foreground="#666")
        self.root.update_idletasks()
        try:
            ruta = generador.generar(datos, self.config)
        except Exception as e:
            self.estado.config(text="")
            messagebox.showerror("Error al generar", str(e))
            return

        self.estado.config(text=f"Listo: {os.path.basename(ruta)}", foreground="#1f7a1f")
        self._abrir_pdf(ruta)

    def _abrir_pdf(self, ruta):
        try:
            if sys.platform.startswith("darwin"):
                os.system(f'open "{ruta}"')
            elif os.name == "nt":
                os.startfile(ruta)  # type: ignore[attr-defined]
            else:
                webbrowser.open(f"file://{ruta}")
        except Exception:
            pass


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
