# -*- coding: utf-8 -*-
"""
Simulador de Distribuciones Discretas (interfaz alternativa)
Autor: Reescrito para Alan
Fecha: 2025
"""
import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ---------------------------
# Funciones de generación
# ---------------------------
def generar_distribucion(nombre, params, sample_size=1000):
    """Genera datos y título según la distribución seleccionada."""
    if nombre == "Uniforme":
        a = int(params["a"].get())
        b = int(params["b"].get())
        data = np.random.randint(a, b + 1, sample_size)
        titulo = f"UNIFORME DISCRETA (a={a}, b={b})"
    elif nombre == "Bernoulli":
        p = float(params["p"].get())
        data = np.random.binomial(1, p, sample_size)
        titulo = f"BERNOULLI (p={p})"
    elif nombre == "Binomial":
        n_trials = int(params["n"].get())
        p = float(params["p"].get())
        data = np.random.binomial(n_trials, p, sample_size)
        titulo = f"BINOMIAL (n={n_trials}, p={p})"
    elif nombre == "Poisson":
        lam = float(params["lam"].get())
        data = np.random.poisson(lam, sample_size)
        titulo = f"POISSON (λ={lam})"
    else:
        data = np.array([])
        titulo = ""
    return data, titulo

# ---------------------------
# UI dinámico de parámetros
# ---------------------------
def limpiar_params():
    for w in params_container.winfo_children():
        w.destroy()

def crear_spin_param(label_text, var, row, from_, to, step=None):
    lbl = ttk.Label(params_container, text=label_text)
    lbl.grid(row=row, column=0, sticky="e", padx=6, pady=6)
    if isinstance(var, tk.IntVar):
        sb = ttk.Spinbox(params_container, from_=from_, to=to, textvariable=var, width=10)
    else:
        # float value -> use Entry with validation
        sb = ttk.Entry(params_container, textvariable=var, width=12)
    sb.grid(row=row, column=1, sticky="w", padx=6, pady=6)
    return sb

def actualizar_parametros(event=None):
    limpiar_params()
    distrib = distrib_combo.get()
    # reset dictionary
    params_vars.clear()

    if distrib == "Uniforme":
        params_vars["a"] = tk.IntVar(value=1)
        params_vars["b"] = tk.IntVar(value=6)
        crear_spin_param("a", params_vars["a"], 0, -10000, 10000)
        crear_spin_param("b", params_vars["b"], 1, -10000, 10000)

    elif distrib == "Bernoulli":
        params_vars["p"] = tk.StringVar(value="0.6")
        crear_spin_param("p", params_vars["p"], 0, 0.0, 1.0)

    elif distrib == "Binomial":
        params_vars["n"] = tk.IntVar(value=10)
        params_vars["p"] = tk.StringVar(value="0.5")
        crear_spin_param("n", params_vars["n"], 0, 1, 1000)
        crear_spin_param("p", params_vars["p"], 1, 0.0, 1.0)

    elif distrib == "Poisson":
        params_vars["lam"] = tk.StringVar(value="3")
        crear_spin_param("λ", params_vars["lam"], 0, 0.0, 1000.0)

# ---------------------------
# Graficar y mostrar estadísticas
# ---------------------------
def graficar():
    distrib = distrib_combo.get()
    n_samples = sample_size_var.get()
    data, titulo = generar_distribucion(distrib, params_vars, sample_size=n_samples)

    if data.size == 0:
        return

    # limpiar figura
    fig.clf()
    ax = fig.add_subplot(111)

    valores, conteo = np.unique(data, return_counts=True)
    ax.bar(valores, conteo, width=0.6, edgecolor="black")
    ax.set_title(titulo, fontsize=14, fontweight="bold")
    ax.set_xlabel("Valores")
    ax.set_ylabel("Frecuencia")
    ax.grid(True, linestyle="--", alpha=0.5)

    canvas.draw()

    # estadísticas
    mean = np.mean(data)
    var = np.var(data, ddof=0)
    stats_text.set(f"Muestras: {n_samples}\nMedia: {mean:.4f}\nVarianza: {var:.4f}")

# ---------------------------
# Construcción de la ventana
# ---------------------------
root = tk.Tk()
root.title("Simulador — interfaz alternativa")
root.geometry("1000x650")
root.configure(bg="#f3f6f8")

# Estilo ttk
style = ttk.Style(root)
style.theme_use("clam")
style.configure("TLabel", background="#e9f2f8", foreground="#0b3d4a", font=("Segoe UI", 10))
style.configure("TButton", font=("Segoe UI", 11, "bold"))
style.configure("TFrame", background="#e9f2f8")

# Layout: left controls, right area (plot + stats)
left_frame = ttk.Frame(root, padding=(12,12,12,12))
left_frame.pack(side="left", fill="y", padx=(12,6), pady=12)

right_frame = ttk.Frame(root, padding=(8,8,8,8))
right_frame.pack(side="right", fill="both", expand=True, padx=(6,12), pady=12)

# ---- Left: título y controles ----
ttk.Label(left_frame, text="Controles", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0,8))

ttk.Label(left_frame, text="Distribución:").grid(row=1, column=0, sticky="w")
distrib_combo = ttk.Combobox(left_frame, values=["Uniforme", "Bernoulli", "Binomial", "Poisson"],
                             state="readonly", width=17)
distrib_combo.set("Uniforme")
distrib_combo.grid(row=1, column=1, sticky="e", pady=6)
distrib_combo.bind("<<ComboboxSelected>>", actualizar_parametros)

# Contenedor de parámetros dinámicos
params_container = ttk.Frame(left_frame, relief="flat")
params_container.grid(row=2, column=0, columnspan=2, pady=(6,10))

# Variables de parámetros
params_vars = {}
actualizar_parametros()

# Sample size control
ttk.Label(left_frame, text="Tamaño de muestra:").grid(row=10, column=0, sticky="w", pady=(10,0))
sample_size_var = tk.IntVar(value=1000)
sample_spin = ttk.Spinbox(left_frame, from_=100, to=20000, increment=100, textvariable=sample_size_var, width=12)
sample_spin.grid(row=10, column=1, sticky="e", pady=(10,0))

# Botón generar
generate_btn = ttk.Button(left_frame, text="Generar y Graficar", command=graficar)
generate_btn.grid(row=11, column=0, columnspan=2, pady=(14,6), ipadx=6, ipady=6)

# Separador y nota
sep = ttk.Separator(left_frame, orient="horizontal")
sep.grid(row=12, column=0, columnspan=2, sticky="ew", pady=8)

ttk.Label(left_frame, text="Interfaz alternativa — controles agrupados", wraplength=160).grid(row=13, column=0, columnspan=2)

# ---- Right: gráfico y estadísticas ----
# Área de título grande
title_frame = ttk.Frame(right_frame)
title_frame.pack(fill="x", pady=(0,6))
ttk.Label(title_frame, text="Visualizador", font=("Segoe UI", 16, "bold")).pack(side="left")

# Figura matplotlib
fig = plt.Figure(figsize=(7.5, 4.6), dpi=100, facecolor="#ffffff")
canvas = FigureCanvasTkAgg(fig, master=right_frame)
canvas.get_tk_widget().pack(fill="both", expand=True, padx=6, pady=6)

# Tarjeta de estadísticas
stats_frame = ttk.Frame(right_frame, padding=(8,8,8,8), relief="ridge")
stats_frame.pack(fill="x", pady=(6,0))
stats_text = tk.StringVar(value="Muestras: -\nMedia: -\nVarianza: -")
ttk.Label(stats_frame, textvariable=stats_text, font=("Segoe UI", 11)).pack(side="left")

# Inicial plot vacío
fig.clf()
ax = fig.add_subplot(111)
ax.text(0.5, 0.5, "Haz clic en 'Generar y Graficar' para ver la distribución",
        ha="center", va="center", fontsize=12, color="#666666")
ax.axis("off")
canvas.draw()

# Atajos de teclado (Enter para generar)
root.bind("<Return>", lambda e: graficar())

root.mainloop()
