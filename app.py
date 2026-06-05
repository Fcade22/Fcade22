"""
Generador de hojas membretadas - Interfaz grafica.

Abrir con doble clic (o ejecutar: python app.py).
Cargas los datos en el cuadro, apretas "Generar PDF" y listo.
"""

import os
import sys
import threading
import webbrowser
from datetime import date

import tkinter as tk
from tkinter import ttk, messagebox

import generador


class App:
    def __init__(self, root):
        self.root = root
        root.title("Generador de Hojas Membretadas")
        root.geometry("520x420")
        root.resizable(False, False)

        try:
            self.config = generador.cargar_config()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer config.json:\n{e}")
            self.config = {}

        cont = ttk.Frame(root, padding=24)
        cont.pack(fill="both", expand=True)

        titulo = ttk.Label(cont, text="Nueva hoja membretada",
                           font=("Helvetica", 16, "bold"))
        titulo.grid(row=0, column=0, columnspan=2, pady=(0, 18), sticky="w")

        self.vars = {}
        self._fila(cont, 1, "Fecha", "fecha",
                   valor=date.today().strftime("%d/%m/%Y"))
        self._fila(cont, 2, "Nombre del cliente", "nombre_cliente")
        self._fila(cont, 3, "Producto", "producto")
        self._fila(cont, 4, "Precio", "precio")

        ayuda = ttk.Label(
            cont,
            text="El precio podes escribirlo como numero (ej: 12500) y se formatea solo.",
            foreground="#666666", font=("Helvetica", 8))
        ayuda.grid(row=5, column=0, columnspan=2, pady=(4, 16), sticky="w")

        botones = ttk.Frame(cont)
        botones.grid(row=6, column=0, columnspan=2, sticky="w")

        self.btn_generar = ttk.Button(botones, text="Generar PDF",
                                      command=self.generar)
        self.btn_generar.pack(side="left")

        self.btn_limpiar = ttk.Button(botones, text="Limpiar",
                                      command=self.limpiar)
        self.btn_limpiar.pack(side="left", padx=8)

        self.estado = ttk.Label(cont, text="", foreground="#1f7a1f",
                                font=("Helvetica", 9))
        self.estado.grid(row=7, column=0, columnspan=2, pady=(16, 0), sticky="w")

        root.bind("<Return>", lambda e: self.generar())

    def _fila(self, cont, fila, etiqueta, clave, valor=""):
        ttk.Label(cont, text=etiqueta).grid(row=fila, column=0, sticky="w",
                                            pady=6, padx=(0, 12))
        var = tk.StringVar(value=valor)
        entry = ttk.Entry(cont, textvariable=var, width=38, font=("Helvetica", 11))
        entry.grid(row=fila, column=1, sticky="w", pady=6)
        self.vars[clave] = var

    def limpiar(self):
        for clave, var in self.vars.items():
            var.set(date.today().strftime("%d/%m/%Y") if clave == "fecha" else "")
        self.estado.config(text="")

    def generar(self):
        datos = {clave: var.get().strip() for clave, var in self.vars.items()}

        if not datos.get("nombre_cliente"):
            messagebox.showwarning("Falta un dato", "Ingresa el nombre del cliente.")
            return
        if not datos.get("producto"):
            messagebox.showwarning("Falta un dato", "Ingresa el producto.")
            return

        self.btn_generar.config(state="disabled")
        self.estado.config(text="Generando...", foreground="#666666")
        self.root.update_idletasks()

        try:
            ruta = generador.generar(datos, self.config)
        except Exception as e:
            self.btn_generar.config(state="normal")
            self.estado.config(text="")
            messagebox.showerror("Error al generar", str(e))
            return

        self.btn_generar.config(state="normal")
        self.estado.config(text=f"Listo: {os.path.basename(ruta)}",
                          foreground="#1f7a1f")
        self._abrir_pdf(ruta)

    def _abrir_pdf(self, ruta):
        """Abre el PDF generado con el visor por defecto del sistema."""
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
