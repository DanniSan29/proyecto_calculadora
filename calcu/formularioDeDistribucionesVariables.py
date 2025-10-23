# -*- coding: utf-8 -*-
"""
Simulador de Distribuciones — Interfaz renovada
Autor: Reescrito para Alan
Fecha: 2025
"""
import tkinter as tk
from tkinter import ttk, messagebox
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math
import csv
from io import StringIO

# ---------- Generación de muestras ----------
def generar_muestras(dist, params, cantidad):
    """Genera la lista de valores según la distribución seleccionada.
    Devuelve lista de floats (o vacía si hay error)."""
    valores = []
    if dist == "Uniforme":
        a = float(params["p1"])
        b = float(params["p2"])
        if a >= b:
            raise ValueError("El mínimo debe ser menor que el máximo.")
        valores = [round(random.uniform(a, b), 2) for _ in range(cantidad)]

    elif dist == "k-Erlang":
        k = float(params["p1"])
        theta = float(params["p2"])
        # Mantengo la formula usada originalmente (gammavariate(k, theta/k))
        valores = [round(random.gammavariate(k, theta / k), 2) for _ in range(cantidad)]

    elif dist == "Exponencial":
        lambd = float(params["p1"])
        # En el original se usó gammavariate(1, lambd)
        valores = [round(random.gammavariate(1, lambd), 2) for _ in range(cantidad)]

    elif dist == "Gamma":
        media = float(params["p1"])
        varianza = float(params["p2"])
        if media <= 0 or varianza <= 0:
            raise ValueError("Media y varianza deben ser positivas.")
        forma = (media ** 2) / varianza
        escala = varianza / media
        valores = [round(random.gammavariate(forma, escala), 2) for _ in range(cantidad)]

    elif dist == "Normal":
        media = float(params["p1"])
        varianza = float(params["p2"])
        if varianza < 0:
            raise ValueError("Varianza debe ser no negativa.")
        valores = [round(random.normalvariate(media, math.sqrt(varianza)), 2) for _ in range(cantidad)]

    elif dist == "Weibull":
        forma = float(params["p1"])
        escala = float(params["p2"])
        desplaz = float(params.get("p3") or 0)
        # Mantengo la fórmula original (aunque no es la parametrización estándar)
        valores = [round(desplaz + (escala ** 2) * ((-np.log(1 - random.random())) ** (1 / forma)), 2)
                   for _ in range(cantidad)]

    return valores

# ---------- Interfaz / UI helpers ----------
class DistribSimulator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador de Distribuciones — Interfaz renovada")
        self.geometry("1100x700")
        self.configure(bg="#f4f7fb")
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except:
            pass

        # Layout: izquierda controls, derecha contenido (tabla + graf)
        self.left = ttk.Frame(self, padding=12)
        self.left.pack(side="left", fill="y")

        self.right = ttk.Frame(self, padding=8)
        self.right.pack(side="right", fill="both", expand=True)

        self._build_controls()
        self._build_table_and_graph()

    def _build_controls(self):
        ttk.Label(self.left, text="Controles", font=("Segoe UI", 14, "bold")).pack(pady=(0,8))

        # Distribución
        ttk.Label(self.left, text="Tipo de distribución:").pack(anchor="w")
        self.combo = ttk.Combobox(self.left, values=["Uniforme", "k-Erlang", "Exponencial", "Gamma", "Normal", "Weibull"],
                                  state="readonly", width=22)
        self.combo.current(0)
        self.combo.pack(pady=6)
        self.combo.bind("<<ComboboxSelected>>", lambda e: self._update_param_fields())

        # Parámetros dinámicos
        self.params_frame = ttk.Frame(self.left)
        self.params_frame.pack(fill="x", pady=(6,10))
        self.p1_var = tk.StringVar()
        self.p2_var = tk.StringVar()
        self.p3_var = tk.StringVar()
        # Field widgets placeholders
        self.lbl_p1 = ttk.Label(self.params_frame, text="Mínimo (a):")
        self.ent_p1 = ttk.Entry(self.params_frame, textvariable=self.p1_var, width=20)
        self.lbl_p2 = ttk.Label(self.params_frame, text="Máximo (b):")
        self.ent_p2 = ttk.Entry(self.params_frame, textvariable=self.p2_var, width=20)
        self.lbl_p3 = ttk.Label(self.params_frame, text="Desplazamiento (opcional):")
        self.ent_p3 = ttk.Entry(self.params_frame, textvariable=self.p3_var, width=20)
        # Inicial
        self.p1_var.set("0"); self.p2_var.set("1"); self.p3_var.set("0")
        self._update_param_fields()

        # Cantidad (Spinbox)
        ttk.Label(self.left, text="Cantidad de valores:").pack(anchor="w", pady=(6,0))
        self.cant_var = tk.IntVar(value=100)
        self.spin_cant = ttk.Spinbox(self.left, from_=1, to=100000, increment=1, textvariable=self.cant_var, width=18)
        self.spin_cant.pack(pady=6)

        # Bins del histograma
        ttk.Label(self.left, text="Bins histograma:").pack(anchor="w")
        self.bins_var = tk.IntVar(value=10)
        self.spin_bins = ttk.Spinbox(self.left, from_=3, to=100, increment=1, textvariable=self.bins_var, width=18)
        self.spin_bins.pack(pady=6)

        # Botones
        btn_frame = ttk.Frame(self.left)
        btn_frame.pack(pady=(10,6), fill="x")
        self.btn_gen = ttk.Button(btn_frame, text="Generar", command=self.generar)
        self.btn_gen.pack(fill="x", pady=4)
        self.btn_export = ttk.Button(btn_frame, text="Exportar CSV (tabla)", command=self.export_csv)
        self.btn_export.pack(fill="x", pady=4)
        self.btn_clear = ttk.Button(btn_frame, text="Limpiar tabla y gráfico", command=self._limpiar_todo)
        self.btn_clear.pack(fill="x", pady=4)

        # Nota rápida / validación
        ttk.Label(self.left, text="* Ingresa parámetros numéricos válidos", foreground="#666666", wraplength=200).pack(pady=(8,0))

    def _update_param_fields(self):
        # Oculta todo y muestra campos según selección
        for w in self.params_frame.winfo_children():
            w.pack_forget()
        dist = self.combo.get()
        if dist == "Uniforme":
            self.lbl_p1.config(text="Mínimo (a):"); self.lbl_p2.config(text="Máximo (b):")
            self.lbl_p1.pack(anchor="w"); self.ent_p1.pack(fill="x", pady=2)
            self.lbl_p2.pack(anchor="w"); self.ent_p2.pack(fill="x", pady=2)

        elif dist == "k-Erlang":
            self.lbl_p1.config(text="Forma (k):"); self.lbl_p2.config(text="Escala (θ):")
            self.lbl_p1.pack(anchor="w"); self.ent_p1.pack(fill="x", pady=2)
            self.lbl_p2.pack(anchor="w"); self.ent_p2.pack(fill="x", pady=2)

        elif dist == "Exponencial":
            self.lbl_p1.config(text="Escala (λ):")
            self.lbl_p1.pack(anchor="w"); self.ent_p1.pack(fill="x", pady=2)

        elif dist == "Gamma":
            self.lbl_p1.config(text="Media (μ):"); self.lbl_p2.config(text="Varianza (σ²):")
            self.lbl_p1.pack(anchor="w"); self.ent_p1.pack(fill="x", pady=2)
            self.lbl_p2.pack(anchor="w"); self.ent_p2.pack(fill="x", pady=2)

        elif dist == "Normal":
            self.lbl_p1.config(text="Media (μ):"); self.lbl_p2.config(text="Varianza (σ²):")
            self.lbl_p1.pack(anchor="w"); self.ent_p1.pack(fill="x", pady=2)
            self.lbl_p2.pack(anchor="w"); self.ent_p2.pack(fill="x", pady=2)

        elif dist == "Weibull":
            self.lbl_p1.config(text="Forma (β):"); self.lbl_p2.config(text="Escala (η):"); self.lbl_p3.config(text="Desplazamiento (opcional):")
            self.lbl_p1.pack(anchor="w"); self.ent_p1.pack(fill="x", pady=2)
            self.lbl_p2.pack(anchor="w"); self.ent_p2.pack(fill="x", pady=2)
            self.lbl_p3.pack(anchor="w"); self.ent_p3.pack(fill="x", pady=2)

    def _build_table_and_graph(self):
        # Divide la derecha en dos: arriba tabla (40%) y abajo gráfico (60%)
        top = ttk.Frame(self.right)
        top.pack(side="top", fill="both", expand=False, pady=(0,6))
        bottom = ttk.Frame(self.right)
        bottom.pack(side="bottom", fill="both", expand=True)

        # Tabla con scrollbar
        self.tree_frame = ttk.Frame(top)
        self.tree_frame.pack(fill="both", expand=True)
        self.table_scroll_y = ttk.Scrollbar(self.tree_frame, orient="vertical")
        self.table_scroll_x = ttk.Scrollbar(self.tree_frame, orient="horizontal")
        self.table = ttk.Treeview(self.tree_frame, columns=("N","Valor"), show="headings",
                                  yscrollcommand=self.table_scroll_y.set, xscrollcommand=self.table_scroll_x.set, height=10)
        self.table.heading("N", text="N°"); self.table.heading("Valor", text="Valor")
        self.table.column("N", width=80, anchor="center"); self.table.column("Valor", width=140, anchor="center")
        self.table_scroll_y.config(command=self.table.yview)
        self.table_scroll_x.config(command=self.table.xview)
        self.table_scroll_y.pack(side="right", fill="y")
        self.table_scroll_x.pack(side="bottom", fill="x")
        self.table.pack(fill="both", expand=True)

        # Estadísticas rápidas
        stats_frame = ttk.Frame(top)
        stats_frame.pack(fill="x", pady=(6,0))
        self.stat_label = ttk.Label(stats_frame, text="N: -    Media: -    Varianza: -", foreground="#333333")
        self.stat_label.pack(anchor="w")

        # Gráfico (matplotlib)
        self.fig, self.ax = plt.subplots(figsize=(8,4))
        plt.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.fig, master=bottom)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)

    # ---------- Acciones ----------
    def generar(self):
        # Validaciones básicas
        try:
            cantidad = int(self.cant_var.get())
            if cantidad <= 0:
                raise ValueError("Cantidad debe ser > 0")
        except Exception:
            messagebox.showerror("Error", "Ingrese una cantidad válida (entero positivo).")
            return

        # Preparar parámetros según campos visibles
        dist = self.combo.get()
        params = {"p1": self.p1_var.get(), "p2": self.p2_var.get(), "p3": self.p3_var.get()}

        # Intentar generar y atrapar errores de conversión
        try:
            valores = generar_muestras(dist, params, cantidad)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return
        except Exception:
            messagebox.showerror("Error", "Parámetros inválidos. Revisa los valores ingresados.")
            return

        # Llenar tabla
        for row in self.table.get_children():
            self.table.delete(row)
        for i, v in enumerate(valores, start=1):
            self.table.insert("", "end", values=(i, v))

        # Actualizar estadísticas
        arr = np.array(valores) if valores else np.array([])
        if arr.size > 0:
            media = float(np.mean(arr))
            var = float(np.var(arr))
            self.stat_label.config(text=f"N: {arr.size}    Media: {media:.4f}    Varianza: {var:.4f}")
        else:
            self.stat_label.config(text="N: 0    Media: -    Varianza: -")

        # Mostrar gráfico
        self._mostrar_grafico(valores, dist)

    def _mostrar_grafico(self, valores, titulo):
        # Limpiar figura
        self.ax.clear()
        if not valores:
            self.ax.text(0.5, 0.5, "No hay datos. Genera valores para ver el histograma.",
                         ha="center", va="center", fontsize=12, color="#666666")
            self.ax.axis("off")
            self.canvas.draw()
            return

        bins = int(self.bins_var.get() or 10)
        n, bins_edges, patches = self.ax.hist(valores, bins=bins, edgecolor="black", rwidth=0.9)
        # Etiquetas de frecuencia encima de las barras
        for i in range(len(n)):
            height = n[i]
            if height >= 1:
                x = bins_edges[i] + (bins_edges[i+1] - bins_edges[i]) / 2
                self.ax.text(x, height + max(n)*0.01, str(int(height)), ha="center", va="bottom", fontsize=8)
        self.ax.set_title(f"Distribución {titulo}", fontsize=13, fontweight="bold")
        self.ax.set_xlabel("Valores"); self.ax.set_ylabel("Frecuencia")
        self.ax.grid(axis='y', linestyle='--', alpha=0.6)
        self.canvas.draw()

    def export_csv(self):
        # Genera CSV en memoria con la tabla actual y muestra diálogo para guardar si hay datos
        rows = list(self.table.get_children())
        if not rows:
            messagebox.showinfo("Exportar CSV", "No hay datos para exportar.")
            return
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["N°", "Valor"])
        for item in rows:
            writer.writerow(self.table.item(item, "values"))
        contenido = output.getvalue()
        output.close()

        # Diálogo simple de guardar (usamos filedialog)
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")], title="Guardar CSV")
        if filename:
            with open(filename, "w", newline='', encoding="utf-8") as f:
                f.write(contenido)
            messagebox.showinfo("Exportar CSV", f"Archivo guardado en:\n{filename}")

    def _limpiar_todo(self):
        for r in self.table.get_children():
            self.table.delete(r)
        self.ax.clear()
        self.ax.text(0.5, 0.5, "Histograma vacío.", ha="center", va="center", color="#666")
        self.ax.axis("off")
        self.canvas.draw()
        self.stat_label.config(text="N: -    Media: -    Varianza: -")

if __name__ == "__main__":
    app = DistribSimulator()
    app.mainloop()
