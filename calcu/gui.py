import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from generadores.cuadrados_medios import cuadrados_medios
from generadores.productos_medios import productos_medios
from generadores.multiplicador_constante import multiplicador_constante

from pruebas.prueba_medias import prueba_medias
from pruebas.prueba_varianza import prueba_varianza
from pruebas.prueba_uniformidad import prueba_uniformidad

class CalculadoraRNG(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculadora RNG - Tkinter")
        self.geometry("1100x700")
        self.xs = []
        self.us = []
        self._build_ui()

    def _build_ui(self):
        menubar = tk.Menu(self)
        archivo = tk.Menu(menubar, tearoff=0)
        archivo.add_command(label="Exportar Números...", command=self.exportar_numeros)
        archivo.add_command(label="Exportar Resultados...", command=self.exportar_resultados)
        archivo.add_separator()
        archivo.add_command(label="Salir", command=self.destroy)
        menubar.add_cascade(label="Archivo", menu=archivo)
        self.config(menu=menubar)

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        tab_gen = ttk.Frame(nb)
        tab_pruebas = ttk.Frame(nb)
        tab_vars = ttk.Frame(nb)

        nb.add(tab_gen, text="Generadores")
        nb.add(tab_pruebas, text="Pruebas")
        nb.add(tab_vars, text="Variables")

        # Generadores
        pad = {'padx':6, 'pady':6}
        ttk.Label(tab_gen, text="Algoritmo:").grid(row=0, column=0, sticky="w", **pad)
        self.alg = tk.StringVar(value="cuadrados_medios")
        ttk.Combobox(tab_gen, textvariable=self.alg, state="readonly", values=["cuadrados_medios","productos_medios","multiplicador_constante"]).grid(row=0, column=1, **pad)

        ttk.Label(tab_gen, text="n:").grid(row=1, column=0, sticky="w", **pad)
        self.n_var = tk.StringVar(value="1000")
        ttk.Entry(tab_gen, textvariable=self.n_var, width=12).grid(row=1, column=1, **pad)

        ttk.Label(tab_gen, text="d (dígitos):").grid(row=1, column=2, sticky="w", **pad)
        self.d_var = tk.StringVar(value="4")
        ttk.Entry(tab_gen, textvariable=self.d_var, width=12).grid(row=1, column=3, **pad)

        ttk.Label(tab_gen, text="Semilla 1:").grid(row=2, column=0, sticky="w", **pad)
        self.sem1 = tk.StringVar(value="1234")
        ttk.Entry(tab_gen, textvariable=self.sem1, width=12).grid(row=2, column=1, **pad)

        ttk.Label(tab_gen, text="Semilla 2:").grid(row=2, column=2, sticky="w", **pad)
        self.sem2 = tk.StringVar(value="5678")
        ttk.Entry(tab_gen, textvariable=self.sem2, width=12).grid(row=2, column=3, **pad)

        ttk.Label(tab_gen, text="Multiplicador c:").grid(row=3, column=0, sticky="w", **pad)
        self.c_var = tk.StringVar(value="2467")
        ttk.Entry(tab_gen, textvariable=self.c_var, width=12).grid(row=3, column=1, **pad)

        ttk.Button(tab_gen, text="Generar", command=self.generar).grid(row=3, column=2, **pad)
        ttk.Button(tab_gen, text="Exportar", command=self.exportar_numeros).grid(row=3, column=3, **pad)

        # Tabla
        cols = ("i","x","u")
        self.tree = ttk.Treeview(tab_gen, columns=cols, show="headings", height=12)
        for c in cols:
            self.tree.heading(c, text=c)
        self.tree.grid(row=4, column=0, columnspan=4, sticky="nsew", padx=8, pady=8)
        tab_gen.grid_rowconfigure(4, weight=1)
        tab_gen.grid_columnconfigure(3, weight=1)

        # Histograma
        self.fig = Figure(figsize=(6,3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=tab_gen)
        self.canvas.get_tk_widget().grid(row=5, column=0, columnspan=4, sticky="nsew", padx=8, pady=8)

        # Pruebas tab
        self.chk_med = tk.BooleanVar(value=True)
        self.chk_var = tk.BooleanVar(value=True)
        self.chk_unif = tk.BooleanVar(value=True)
        ttk.Checkbutton(tab_pruebas, text="Medias", variable=self.chk_med).grid(row=0, column=0, sticky="w", **pad)
        ttk.Checkbutton(tab_pruebas, text="Varianza", variable=self.chk_var).grid(row=0, column=1, sticky="w", **pad)
        ttk.Checkbutton(tab_pruebas, text="Uniformidad", variable=self.chk_unif).grid(row=0, column=2, sticky="w", **pad)

        ttk.Label(tab_pruebas, text="alpha:").grid(row=1, column=0, sticky="w", **pad)
        self.alpha = tk.StringVar(value="0.05")
        ttk.Entry(tab_pruebas, textvariable=self.alpha, width=12).grid(row=1, column=1, **pad)

        ttk.Label(tab_pruebas, text="k (uniformidad):").grid(row=1, column=2, sticky="w", **pad)
        self.k_var = tk.StringVar(value="")
        ttk.Entry(tab_pruebas, textvariable=self.k_var, width=12).grid(row=1, column=3, **pad)

        ttk.Button(tab_pruebas, text="Probar", command=self.probar).grid(row=1, column=4, **pad)

        self.txt = tk.Text(tab_pruebas, height=15)
        self.txt.grid(row=2, column=0, columnspan=5, sticky="nsew", padx=8, pady=8)
        tab_pruebas.grid_rowconfigure(2, weight=1)
        tab_pruebas.grid_columnconfigure(4, weight=1)

        # Grafico de frecuencias
        self.fig2 = Figure(figsize=(6,3), dpi=100)
        self.ax2 = self.fig2.add_subplot(111)
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=tab_pruebas)
        self.canvas2.get_tk_widget().grid(row=3, column=0, columnspan=5, sticky="nsew", padx=8, pady=8)

        ttk.Label(tab_vars, text="Espacio para variables aleatorias.").pack(padx=12, pady=12)

    def generar(self):
        try:
            n = int(self.n_var.get())
            d = int(self.d_var.get())
            sem1 = int(self.sem1.get())
            alg = self.alg.get()
            if alg == "cuadrados_medios":
                xs, us = cuadrados_medios(sem1, n, d)
            elif alg == "productos_medios":
                sem2 = int(self.sem2.get())
                xs, us = productos_medios(sem1, sem2, n, d)
            elif alg == "multiplicador_constante":
                c = int(self.c_var.get())
                xs, us = multiplicador_constante(sem1, c, n, d)
            else:
                raise ValueError("Algoritmo no válido.")
            self.xs, self.us = xs, us
            self._refresh_table(xs, us)
            self._plot_hist(us)
            messagebox.showinfo("OK", f"Se generaron {len(us)} números.")
        except Exception as e:
            messagebox.showerror("Error al generar", str(e))

    def _refresh_table(self, xs, us):
        for it in self.tree.get_children():
            self.tree.delete(it)
        for i,(x,u) in enumerate(zip(xs,us), start=1):
            self.tree.insert("", "end", values=(i,x,f"{u:.6f}"))

    def _plot_hist(self, us):
        self.ax.clear()
        if len(us)>0:
            self.ax.hist(us, bins=max(5,int(len(us)**0.5)), range=(0,1))
        self.ax.set_title("Histograma u_i")
        self.canvas.draw()

    def probar(self):
        if not hasattr(self, "us") or not self.us:
            messagebox.showwarning("Atención", "Primero genera números.")
            return
        try:
            alpha = float(self.alpha.get())
            k = int(self.k_var.get()) if self.k_var.get().strip()!="" else None
            self.txt.delete("1.0", "end")
            resultados = {}
            if self.chk_med.get():
                r = prueba_medias(self.us, alpha=alpha)
                resultados['medias'] = r
                self.txt.insert("end", "=== Prueba de Medias ===\n")
                for k,v in r.items():
                    self.txt.insert("end", f"{k}: {v}\n")
            if self.chk_var.get():
                r = prueba_varianza(self.us, alpha=alpha)
                resultados['varianza'] = r
                self.txt.insert("end", "\n=== Prueba de Varianza ===\n")
                for k,v in r.items():
                    self.txt.insert("end", f"{k}: {v}\n")
            if self.chk_unif.get():
                r = prueba_uniformidad(self.us, k=k, alpha=alpha)
                resultados['uniformidad'] = r
                self.txt.insert("end", "\n=== Prueba de Uniformidad ===\n")
                for k,v in r.items():
                    if k in ('frecuencias','intervalos'): continue
                    self.txt.insert("end", f"{k}: {v}\n")
                # plot frecuencias
                self.ax2.clear()
                freqs = r['frecuencias']
                self.ax2.bar(range(1,len(freqs)+1), freqs)
                self.ax2.set_title("Frecuencias observadas")
                self.canvas2.draw()
            self._resultados_cache = resultados
        except Exception as e:
            messagebox.showerror("Error en pruebas", str(e))

    def exportar_numeros(self):
        if not hasattr(self, "us") or not self.us:
            messagebox.showwarning("Atención", "No hay números para exportar.")
            return
        f = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
        if not f: return
        import csv
        with open(f, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["i","x_i","u_i"])
            for i,(x,u) in enumerate(zip(self.xs,self.us), start=1):
                w.writerow([i,x,f"{u:.10f}"])
        messagebox.showinfo("Exportar", "Archivo guardado.")

    def exportar_resultados(self):
        if not hasattr(self, "_resultados_cache") or not self._resultados_cache:
            messagebox.showwarning("Atención", "No hay resultados para exportar.")
            return
        f = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON","*.json")])
        if not f: return
        import json
        with open(f, "w", encoding="utf-8") as fh:
            json.dump(self._resultados_cache, fh, ensure_ascii=False, indent=2)
        messagebox.showinfo("Exportar", "Resultados guardados.")

def run():
    app = CalculadoraRNG()
    app.mainloop()

if __name__ == "__main__":
    run()
