# -*- coding: utf-8 -*-
"""
Juego de la Vida — Interfaz alternativa
Autor: Reescrito para Alan (2025)
Descripción: Misma lógica funcional que el script original pero con una
interfaz reorganizada: panel de controles lateral con opciones (filas,
columnas, tamaño de celda, velocidad), botones modernos, contador de
generaciones y presets (aleatorio / limpiar / paso a paso / reiniciar).
Se mantiene la detección de "esquina alcanzada" y el comportamiento
original.
"""
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import random
import math

class GameOfLifeUI:
    def __init__(self, root,
                 rows=20, cols=20, cell_size=20, init_prob=0.2):
        self.root = root
        self.root.title("Juego de la Vida — Interfaz alternativa")

        # Parámetros
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.init_prob = init_prob
        self.running = False
        self.generation = 0
        self.alive_color = "#111111"
        self.bg_color = "#d0ebff"
        self.grid_color = "#c0c0c0"

        # Estado de la cuadrícula (0/1)
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

        # Layout: izquierdo controles, derecho canvas
        self.main_frame = ttk.Frame(root, padding=8)
        self.main_frame.pack(fill="both", expand=True)

        self.controls_frame = ttk.Frame(self.main_frame)
        self.controls_frame.pack(side="left", fill="y", padx=(0,8))

        self.canvas_frame = ttk.Frame(self.main_frame)
        self.canvas_frame.pack(side="right", fill="both", expand=True)

        # Controls
        ttk.Label(self.controls_frame, text="Controles", font=(None, 12, "bold")).pack(pady=(4,8))

        # Filas / Columnas
        rc_frame = ttk.Frame(self.controls_frame)
        rc_frame.pack(fill="x", pady=4)
        ttk.Label(rc_frame, text="Filas:").grid(row=0, column=0, sticky="w")
        self.rows_var = tk.IntVar(value=self.rows)
        self.rows_sb = ttk.Spinbox(rc_frame, from_=5, to=200, textvariable=self.rows_var, width=7,
                                   command=self._apply_size_change)
        self.rows_sb.grid(row=0, column=1, padx=6)

        ttk.Label(rc_frame, text="Columnas:").grid(row=1, column=0, sticky="w")
        self.cols_var = tk.IntVar(value=self.cols)
        self.cols_sb = ttk.Spinbox(rc_frame, from_=5, to=200, textvariable=self.cols_var, width=7,
                                   command=self._apply_size_change)
        self.cols_sb.grid(row=1, column=1, padx=6)

        # Tamaño de celda
        ttk.Label(self.controls_frame, text="Tamaño celda:").pack(anchor="w", pady=(8,0))
        self.cell_var = tk.IntVar(value=self.cell_size)
        self.cell_scale = ttk.Scale(self.controls_frame, from_=6, to=50, orient="horizontal",
                                    variable=self.cell_var, command=self._apply_size_change)
        self.cell_scale.pack(fill="x", pady=4)

        # Probabilidad inicial
        ttk.Label(self.controls_frame, text="Prob. inicio (0-1):").pack(anchor="w", pady=(8,0))
        self.prob_var = tk.DoubleVar(value=self.init_prob)
        self.prob_entry = ttk.Entry(self.controls_frame, textvariable=self.prob_var, width=10)
        self.prob_entry.pack(pady=4)

        # Velocidad
        ttk.Label(self.controls_frame, text="Velocidad (ms):").pack(anchor="w", pady=(8,0))
        self.speed_var = tk.IntVar(value=200)
        self.speed_scale = ttk.Scale(self.controls_frame, from_=50, to=1000, orient="horizontal",
                                     variable=self.speed_var)
        self.speed_scale.pack(fill="x", pady=4)

        # Color alive
        cframe = ttk.Frame(self.controls_frame)
        cframe.pack(fill="x", pady=(8,2))
        self.color_btn = ttk.Button(cframe, text="Color célula", command=self._choose_alive_color)
        self.color_btn.grid(row=0, column=0, sticky="w")
        self.reset_color_btn = ttk.Button(cframe, text="Rest. colores", command=self._reset_colors)
        self.reset_color_btn.grid(row=0, column=1, padx=6)

        # Botones principales
        btns = ttk.Frame(self.controls_frame)
        btns.pack(pady=(12,6))
        self.start_btn = ttk.Button(btns, text="▶ Iniciar", command=self.start)
        self.start_btn.grid(row=0, column=0, padx=4, pady=4)
        self.stop_btn = ttk.Button(btns, text="⏸ Detener", command=self.stop)
        self.stop_btn.grid(row=0, column=1, padx=4, pady=4)
        self.step_btn = ttk.Button(btns, text="⤸ Paso", command=self.step_once)
        self.step_btn.grid(row=1, column=0, padx=4, pady=4)
        self.clear_btn = ttk.Button(btns, text="✖ Limpiar", command=self.clear)
        self.clear_btn.grid(row=1, column=1, padx=4, pady=4)

        # Aleatorizar y reiniciar
        extras = ttk.Frame(self.controls_frame)
        extras.pack(pady=(6,8))
        self.random_btn = ttk.Button(extras, text="🔀 Aleatorio", command=self.randomize_grid)
        self.random_btn.grid(row=0, column=0, padx=4)
        self.restart_btn = ttk.Button(extras, text="↺ Reiniciar", command=self.reset)
        self.restart_btn.grid(row=0, column=1, padx=4)

        # Información / estadísticas
        info = ttk.Frame(self.controls_frame)
        info.pack(fill="x", pady=(8,0))
        self.gen_label = ttk.Label(info, text=f"Generación: {self.generation}")
        self.gen_label.pack(anchor="w")
        self.count_label = ttk.Label(info, text="Células vivas: 0")
        self.count_label.pack(anchor="w")

        # Canvas para la cuadrícula
        self.canvas = tk.Canvas(self.canvas_frame, bg=self.bg_color)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self._on_canvas_click)

        # Resizable behavior
        self.canvas_frame.bind("<Configure>", self._on_canvas_resize)

        # Inicializar
        self._rebuild_grid_struct()
        self.randomize_grid()
        self._draw_grid()

    # ------------------ utilidades de interfaz ------------------
    def _apply_size_change(self, *args):
        # Aplicar cambio en filas/cols/tamaño y reconstruir la estructura
        try:
            new_rows = int(self.rows_var.get())
            new_cols = int(self.cols_var.get())
        except Exception:
            return
        new_cell = int(self.cell_var.get())
        # límites razonables para evitar canvas gigantes
        max_dim = max(5, min(200, new_rows))
        max_c = max(5, min(200, new_cols))
        self.rows, self.cols = max_dim, max_c
        self.cell_size = max(6, min(100, new_cell))
        self._rebuild_grid_struct()
        self._draw_grid()

    def _choose_alive_color(self):
        c = colorchooser.askcolor(title="Elige color para células vivas", initialcolor=self.alive_color)
        if c and c[1]:
            self.alive_color = c[1]
            self._draw_grid()

    def _reset_colors(self):
        self.alive_color = "#111111"
        self.bg_color = "#d0ebff"
        self.canvas.configure(bg=self.bg_color)
        self._draw_grid()

    def _on_canvas_resize(self, event):
        # redraw para adaptarse al nuevo tamaño
        self._draw_grid()

    # ------------------ lógica de la cuadrícula ------------------
    def _rebuild_grid_struct(self):
        # Asegura que self.grid tenga el tamaño (rows x cols)
        new_grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        # Copiar lo que quepa de la vieja cuadrícula
        for i in range(min(self.rows, len(self.grid))):
            for j in range(min(self.cols, len(self.grid[0]) if self.grid else 0)):
                new_grid[i][j] = self.grid[i][j]
        self.grid = new_grid
        # ajustar tamaño del canvas
        width = self.cols * self.cell_size
        height = self.rows * self.cell_size
        self.canvas.config(width=width, height=height)

    def randomize_grid(self):
        try:
            p = float(self.prob_var.get())
        except Exception:
            p = self.init_prob
            self.prob_var.set(p)
        for i in range(self.rows):
            for j in range(self.cols):
                self.grid[i][j] = 1 if random.random() < p else 0
        self.generation = 0
        self._update_info()

    def clear(self):
        self.running = False
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.generation = 0
        self._draw_grid()
        self._update_info()

    def reset(self):
        self.running = False
        self._rebuild_grid_struct()
        self.randomize_grid()
        self._draw_grid()

    def _on_canvas_click(self, event):
        col = event.x // self.cell_size
        row = event.y // self.cell_size
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.grid[row][col] = 1 - self.grid[row][col]
            self._draw_grid()
            self._update_info()

    def _draw_grid(self):
        self.canvas.delete("cell")
        alive_count = 0
        for i in range(self.rows):
            for j in range(self.cols):
                x1 = j * self.cell_size
                y1 = i * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                if self.grid[i][j] == 1:
                    alive_count += 1
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill=self.alive_color,
                                                 width=0, tags=("cell", "alive"))
                else:
                    # Solo para mantener fondo uniforme; no se dibuja rect para 0
                    pass
                # línea de la cuadrícula (delgada)
                self.canvas.create_rectangle(x1, y1, x2, y2, outline=self.grid_color, width=1, tags="gridline")
        self._update_info(alive_count)

    def _update_info(self, alive_count=None):
        if alive_count is None:
            alive_count = sum(sum(row) for row in self.grid)
        self.gen_label.config(text=f"Generación: {self.generation}")
        self.count_label.config(text=f"Células vivas: {alive_count}")

    # ------------------ motor del juego ------------------
    def start(self):
        if not self.running:
            self.running = True
            self._run()

    def stop(self):
        self.running = False

    def step_once(self):
        # Ejecuta una sola iteración
        self._iterate()
        self._draw_grid()

    def _run(self):
        if not self.running:
            return
        self._iterate()
        self._draw_grid()
        # detectar esquinas alcanzadas
        if self._check_corner_hit():
            self.running = False
            if messagebox.askyesno("Esquina alcanzada", "¡Una célula llegó a la esquina!\n¿Desea reiniciar?"):
                self.reset()
        else:
            delay = max(10, int(self.speed_var.get()))
            self.root.after(delay, self._run)

    def _iterate(self):
        new_grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        for i in range(self.rows):
            for j in range(self.cols):
                alive_neighbors = self._count_neighbors(i, j)
                if self.grid[i][j] == 1:
                    new_grid[i][j] = 1 if alive_neighbors in (2, 3) else 0
                else:
                    new_grid[i][j] = 1 if alive_neighbors == 3 else 0
        self.grid = new_grid
        self.generation += 1

    def _count_neighbors(self, i, j):
        count = 0
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                if di == 0 and dj == 0:
                    continue
                ni, nj = i + di, j + dj
                if 0 <= ni < self.rows and 0 <= nj < self.cols:
                    count += self.grid[ni][nj]
        return count

    def _check_corner_hit(self):
        corners = [(0, 0), (0, self.cols - 1), (self.rows - 1, 0), (self.rows - 1, self.cols - 1)]
        for (i, j) in corners:
            if self.grid[i][j] == 1:
                return True
        return False

# ------------------ ejecución principal ------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = GameOfLifeUI(root, rows=20, cols=20, cell_size=25, init_prob=0.2)
    root.mainloop()
