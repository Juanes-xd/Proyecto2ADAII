"""GUI de escritorio para el problema MinPol (Tkinter, sin dependencias externas).

Responsabilidades cubiertas (parte GUI del proyecto):
  - Formulario para configurar la entrada (n, m, p, v, ce, matriz de costos c, ct, MaxMovs).
  - Cargar una entrada existente desde un archivo .mpl (Sección 3.1 del enunciado).
  - Botón único que: genera DatosProyecto.dzn, ejecuta Proyecto.mzn y despliega la solución.
"""
from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

import dzn_io
import minizinc_runner
import mpl_io

ROOT = Path(__file__).resolve().parents[1]
DZN_OUTPUT_PATH = ROOT / "DatosProyecto.dzn"

DEFAULT_EXAMPLE = {
    "n": 20,
    "m": 5,
    "p": [12, 4, 0, 4, 0],
    "v": [0.0, 0.25, 0.5, 0.75, 1.0],
    "ce": [1.0, 2.0, 1.0, 1.0, 3.0],
    "c": [
        [0.0, 2.0, 4.0, 5.0, 7.0],
        [1.0, 0.0, 3.0, 4.0, 6.0],
        [3.0, 2.0, 0.0, 2.0, 4.0],
        [4.0, 2.0, 1.0, 0.0, 2.0],
        [8.0, 5.0, 3.0, 2.0, 0.0],
    ],
    "ct": 20.0,
    "max_movs": 18,
}


class ScrollableFrame(ttk.Frame):
    """Frame con scroll vertical/horizontal, usado para la matriz de costos."""

    def __init__(self, parent, height=220, **kwargs):
        super().__init__(parent, **kwargs)
        self.canvas = tk.Canvas(self, borderwidth=0, height=height, highlightthickness=0)
        self.vbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.hbar = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.inner = ttk.Frame(self.canvas)

        self.inner.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.vbar.set, xscrollcommand=self.hbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.vbar.grid(row=0, column=1, sticky="ns")
        self.hbar.grid(row=1, column=0, sticky="ew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)


class MinPolApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MinPol - Interfaz gráfica (Proyecto II - ADA II)")
        self.geometry("1180x820")
        self.minsize(1000, 700)

        self.m_var = tk.IntVar(value=DEFAULT_EXAMPLE["m"])
        self.n_var = tk.StringVar(value=str(DEFAULT_EXAMPLE["n"]))
        self.ct_var = tk.StringVar(value=str(DEFAULT_EXAMPLE["ct"]))
        self.max_movs_var = tk.StringVar(value=str(DEFAULT_EXAMPLE["max_movs"]))
        self.solver_var = tk.StringVar(value="gecode")
        self.time_limit_var = tk.StringVar(value="30")

        self.opinion_entries: list[dict] = []   # una entrada por opinión: {p, v, ce}
        self.cost_entries: list[list[tk.Entry]] = []

        self._build_layout()
        self._regenerate_table(initial_data=DEFAULT_EXAMPLE)

    # ------------------------------------------------------------------ UI
    def _build_layout(self):
        outer = ttk.Panedwindow(self, orient="horizontal")
        outer.pack(fill="both", expand=True, padx=8, pady=8)

        left = ttk.Frame(outer)
        right = ttk.Frame(outer)
        outer.add(left, weight=3)
        outer.add(right, weight=2)

        self._build_form(left)
        self._build_results(right)

    def _build_form(self, parent):
        top_bar = ttk.Frame(parent)
        top_bar.pack(fill="x", pady=(0, 6))
        ttk.Button(top_bar, text="Cargar entrada (.mpl)", command=self.load_mpl_file).pack(side="left")
        ttk.Button(top_bar, text="Cargar ejemplo del enunciado", command=self.load_default_example).pack(side="left", padx=6)
        ttk.Button(top_bar, text="Limpiar formulario", command=self.clear_form).pack(side="left")

        header = ttk.LabelFrame(parent, text="Parámetros generales")
        header.pack(fill="x", pady=4)

        ttk.Label(header, text="n (nº personas):").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        ttk.Entry(header, textvariable=self.n_var, width=10).grid(row=0, column=1, sticky="w", padx=4)

        ttk.Label(header, text="m (nº opiniones):").grid(row=0, column=2, sticky="w", padx=4, pady=4)
        self.m_spin = ttk.Spinbox(header, from_=2, to=20, textvariable=self.m_var, width=6,
                                   command=lambda: self._regenerate_table())
        self.m_spin.grid(row=0, column=3, sticky="w", padx=4)
        ttk.Button(header, text="Generar tabla", command=lambda: self._regenerate_table()).grid(
            row=0, column=4, sticky="w", padx=6
        )

        ttk.Label(header, text="ct (costo total máx.):").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        ttk.Entry(header, textvariable=self.ct_var, width=10).grid(row=1, column=1, sticky="w", padx=4)

        ttk.Label(header, text="MaxMovs:").grid(row=1, column=2, sticky="w", padx=4, pady=4)
        ttk.Entry(header, textvariable=self.max_movs_var, width=10).grid(row=1, column=3, sticky="w", padx=4)

        # ---- tabla de opiniones: p, v, ce ----
        opinions_frame = ttk.LabelFrame(parent, text="Opiniones: personas iniciales (p), valor ideológico (v), costo extra (ce)")
        opinions_frame.pack(fill="x", pady=6)
        self.opinions_container = ttk.Frame(opinions_frame)
        self.opinions_container.pack(fill="x", padx=4, pady=4)

        # ---- matriz de costos c ----
        cost_frame = ttk.LabelFrame(parent, text="Matriz de costos c[i][j] (fila = origen i, columna = destino j)")
        cost_frame.pack(fill="both", expand=True, pady=6)
        self.cost_scroll = ScrollableFrame(cost_frame, height=260)
        self.cost_scroll.pack(fill="both", expand=True, padx=4, pady=4)

        # ---- ejecución ----
        exec_frame = ttk.LabelFrame(parent, text="Ejecución del modelo")
        exec_frame.pack(fill="x", pady=6)

        ttk.Label(exec_frame, text="Solver:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.solver_combo = ttk.Combobox(exec_frame, textvariable=self.solver_var, width=14,
                                          values=minizinc_runner.list_available_solvers())
        self.solver_combo.grid(row=0, column=1, sticky="w", padx=4)

        ttk.Label(exec_frame, text="Límite de tiempo (s):").grid(row=0, column=2, sticky="w", padx=4, pady=4)
        ttk.Entry(exec_frame, textvariable=self.time_limit_var, width=8).grid(row=0, column=3, sticky="w", padx=4)

        btns = ttk.Frame(exec_frame)
        btns.grid(row=1, column=0, columnspan=4, sticky="w", padx=4, pady=(8, 4))
        ttk.Button(btns, text="Solo generar DatosProyecto.dzn", command=self.on_generate_only).pack(side="left")
        self.run_button = ttk.Button(btns, text="Generar y ejecutar modelo", command=self.on_generate_and_run)
        self.run_button.pack(side="left", padx=8)

        self.status_label = ttk.Label(exec_frame, text="Listo.", foreground="#333")
        self.status_label.grid(row=2, column=0, columnspan=4, sticky="w", padx=4, pady=(0, 4))

    def _build_results(self, parent):
        summary_frame = ttk.LabelFrame(parent, text="Resultado")
        summary_frame.pack(fill="x", pady=4)

        self.result_vars = {
            "estado": tk.StringVar(value="—"),
            "polarizacion": tk.StringVar(value="—"),
            "mediana": tk.StringVar(value="—"),
            "costo_usado": tk.StringVar(value="—"),
            "movimientos_usados": tk.StringVar(value="—"),
            "personas_movidas": tk.StringVar(value="—"),
            "tiempo": tk.StringVar(value="—"),
            "solver_modelo": tk.StringVar(value="—"),
        }

        labels = [
            ("Estado:", "estado"),
            ("Polarización final:", "polarizacion"),
            ("Mediana:", "mediana"),
            ("Costo usado / ct:", "costo_usado"),
            ("Movimientos usados / MaxMovs:", "movimientos_usados"),
            ("Personas movidas:", "personas_movidas"),
            ("Tiempo de ejecución:", "tiempo"),
            ("Modelo / solver:", "solver_modelo"),
        ]
        for row, (text, key) in enumerate(labels):
            ttk.Label(summary_frame, text=text).grid(row=row, column=0, sticky="w", padx=4, pady=2)
            ttk.Label(summary_frame, textvariable=self.result_vars[key], font=("TkDefaultFont", 10, "bold")).grid(
                row=row, column=1, sticky="w", padx=4, pady=2
            )

        dist_frame = ttk.LabelFrame(parent, text="Distribución final por opinión")
        dist_frame.pack(fill="x", pady=4)
        self.dist_tree = ttk.Treeview(dist_frame, columns=("opinion", "personas"), show="headings", height=6)
        self.dist_tree.heading("opinion", text="Opinión")
        self.dist_tree.heading("personas", text="Personas finales")
        self.dist_tree.pack(fill="x", padx=4, pady=4)

        moves_frame = ttk.LabelFrame(parent, text="Movimientos realizados")
        moves_frame.pack(fill="both", expand=True, pady=4)
        self.moves_tree = ttk.Treeview(moves_frame, columns=("origen", "destino", "personas"), show="headings", height=8)
        self.moves_tree.heading("origen", text="Origen")
        self.moves_tree.heading("destino", text="Destino")
        self.moves_tree.heading("personas", text="Personas movidas")
        self.moves_tree.pack(fill="both", expand=True, padx=4, pady=4)

        raw_frame = ttk.LabelFrame(parent, text="Salida cruda de MiniZinc")
        raw_frame.pack(fill="both", expand=True, pady=4)
        self.raw_text = ScrolledText(raw_frame, height=10, wrap="word")
        self.raw_text.pack(fill="both", expand=True, padx=4, pady=4)

    # ------------------------------------------------------------ tabla m
    def _regenerate_table(self, initial_data: dict | None = None):
        try:
            m = int(self.m_var.get())
        except (tk.TclError, ValueError):
            messagebox.showerror("Error", "m debe ser un entero válido")
            return
        if m < 2:
            messagebox.showerror("Error", "m debe ser al menos 2")
            return

        for widget in self.opinions_container.winfo_children():
            widget.destroy()
        for widget in self.cost_scroll.inner.winfo_children():
            widget.destroy()

        self.opinion_entries = []
        self.cost_entries = []

        headers = ["Opinión", "p (personas)", "v (valor)", "ce (costo extra)"]
        for col, text in enumerate(headers):
            ttk.Label(self.opinions_container, text=text, font=("TkDefaultFont", 9, "bold")).grid(
                row=0, column=col, padx=4, pady=2
            )

        p_default = initial_data["p"] if initial_data else [0] * m
        v_default = initial_data["v"] if initial_data else [0.0] * m
        ce_default = initial_data["ce"] if initial_data else [0.0] * m

        for i in range(m):
            ttk.Label(self.opinions_container, text=f"Op. {i + 1}").grid(row=i + 1, column=0, padx=4, pady=2)
            p_entry = ttk.Entry(self.opinions_container, width=10)
            p_entry.insert(0, str(p_default[i]) if i < len(p_default) else "0")
            p_entry.grid(row=i + 1, column=1, padx=4, pady=2)

            v_entry = ttk.Entry(self.opinions_container, width=10)
            v_entry.insert(0, str(v_default[i]) if i < len(v_default) else "0.0")
            v_entry.grid(row=i + 1, column=2, padx=4, pady=2)

            ce_entry = ttk.Entry(self.opinions_container, width=10)
            ce_entry.insert(0, str(ce_default[i]) if i < len(ce_default) else "0.0")
            ce_entry.grid(row=i + 1, column=3, padx=4, pady=2)

            self.opinion_entries.append({"p": p_entry, "v": v_entry, "ce": ce_entry})

        # matriz de costos
        c_default = initial_data["c"] if initial_data else [[0.0] * m for _ in range(m)]
        ttk.Label(self.cost_scroll.inner, text="").grid(row=0, column=0)
        for j in range(m):
            ttk.Label(self.cost_scroll.inner, text=f"→ Op.{j + 1}", font=("TkDefaultFont", 9, "bold")).grid(
                row=0, column=j + 1, padx=3, pady=2
            )
        for i in range(m):
            ttk.Label(self.cost_scroll.inner, text=f"Op.{i + 1} →", font=("TkDefaultFont", 9, "bold")).grid(
                row=i + 1, column=0, padx=3, pady=2
            )
            row_entries = []
            for j in range(m):
                entry = ttk.Entry(self.cost_scroll.inner, width=8)
                value = c_default[i][j] if (i < len(c_default) and j < len(c_default[i])) else 0.0
                entry.insert(0, "0.0" if i == j else str(value))
                entry.grid(row=i + 1, column=j + 1, padx=2, pady=2)
                if i == j:
                    entry.configure(state="disabled")
                row_entries.append(entry)
            self.cost_entries.append(row_entries)

        if initial_data:
            self.n_var.set(str(initial_data["n"]))
            self.ct_var.set(str(initial_data["ct"]))
            self.max_movs_var.set(str(initial_data["max_movs"]))

    # ------------------------------------------------------------- acciones
    def load_default_example(self):
        self.m_var.set(DEFAULT_EXAMPLE["m"])
        self._regenerate_table(initial_data=DEFAULT_EXAMPLE)
        self.status_label.configure(text="Ejemplo del enunciado (Sección 2.4) cargado.")

    def clear_form(self):
        m = int(self.m_var.get())
        empty = {
            "n": 0, "m": m, "p": [0] * m, "v": [0.0] * m, "ce": [0.0] * m,
            "c": [[0.0] * m for _ in range(m)], "ct": 0.0, "max_movs": 0,
        }
        self._regenerate_table(initial_data=empty)
        self.status_label.configure(text="Formulario limpiado.")

    def load_mpl_file(self):
        path = filedialog.askopenfilename(
            title="Seleccionar entrada .mpl",
            filetypes=[("Archivos MinPol", "*.mpl"), ("Todos los archivos", "*.*")],
        )
        if not path:
            return
        try:
            data = mpl_io.load_mpl(Path(path))
        except Exception as exc:
            messagebox.showerror("Error al leer .mpl", str(exc))
            return
        self.m_var.set(data["m"])
        self._regenerate_table(initial_data=data)
        self.status_label.configure(text=f"Entrada cargada desde {Path(path).name}")

    def collect_input(self) -> dict:
        try:
            n = int(self.n_var.get())
            m = int(self.m_var.get())
            ct = float(self.ct_var.get())
            max_movs = int(self.max_movs_var.get())
        except ValueError as exc:
            raise ValueError(f"Parámetro general inválido: {exc}") from exc

        p, v, ce = [], [], []
        for idx, row in enumerate(self.opinion_entries):
            try:
                p.append(int(row["p"].get()))
                v.append(float(row["v"].get()))
                ce.append(float(row["ce"].get()))
            except ValueError as exc:
                raise ValueError(f"Fila de opinión {idx + 1} tiene un valor inválido: {exc}") from exc

        c = []
        for i, row_entries in enumerate(self.cost_entries):
            row_values = []
            for j, entry in enumerate(row_entries):
                if i == j:
                    row_values.append(0.0)
                    continue
                try:
                    row_values.append(float(entry.get()))
                except ValueError as exc:
                    raise ValueError(f"Costo c[{i + 1}][{j + 1}] inválido: {exc}") from exc
            c.append(row_values)

        if sum(p) != n:
            raise ValueError(
                f"La suma de p ({sum(p)}) debe ser igual a n ({n}). Corrija n o la distribución p."
            )
        if any(value < 0 for value in p):
            raise ValueError("Los valores de p no pueden ser negativos.")
        if ct < 0:
            raise ValueError("ct no puede ser negativo.")
        if max_movs < 0:
            raise ValueError("MaxMovs no puede ser negativo.")

        return {"n": n, "m": m, "p": p, "v": v, "ce": ce, "c": c, "ct": ct, "max_movs": max_movs}

    def on_generate_only(self):
        try:
            data = self.collect_input()
        except ValueError as exc:
            messagebox.showerror("Entrada inválida", str(exc))
            return
        dzn_io.write_dzn(DZN_OUTPUT_PATH, **data)
        self.status_label.configure(text=f"DatosProyecto.dzn generado en {DZN_OUTPUT_PATH}")
        messagebox.showinfo("Listo", f"Se generó:\n{DZN_OUTPUT_PATH}")

    def on_generate_and_run(self):
        try:
            data = self.collect_input()
        except ValueError as exc:
            messagebox.showerror("Entrada inválida", str(exc))
            return

        dzn_io.write_dzn(DZN_OUTPUT_PATH, **data)
        self.status_label.configure(text="DatosProyecto.dzn generado. Ejecutando modelo…")
        self.run_button.configure(state="disabled")
        self.update_idletasks()

        try:
            time_limit = int(self.time_limit_var.get())
        except ValueError:
            time_limit = 30

        try:
            run_result = minizinc_runner.run_model(
                DZN_OUTPUT_PATH, solver=self.solver_var.get() or "gecode", time_limit_seconds=time_limit
            )
        except (minizinc_runner.MiniZincNotFoundError, minizinc_runner.ModelNotFoundError) as exc:
            self.run_button.configure(state="normal")
            self.status_label.configure(text="Error al ejecutar el modelo.")
            messagebox.showerror("No se pudo ejecutar el modelo", str(exc))
            return
        except Exception as exc:
            self.run_button.configure(state="normal")
            self.status_label.configure(text="Error inesperado al ejecutar el modelo.")
            messagebox.showerror("Error inesperado", str(exc))
            return

        self.run_button.configure(state="normal")
        self.status_label.configure(text=f"Ejecución terminada: {run_result['status']}")
        self._display_results(data, run_result)

    # ------------------------------------------------------------- salida
    def _display_results(self, data: dict, run_result: dict):
        for tree in (self.dist_tree, self.moves_tree):
            for item in tree.get_children():
                tree.delete(item)
        self.raw_text.delete("1.0", "end")
        self.raw_text.insert("end", run_result["raw_output"])

        self.result_vars["estado"].set(run_result["status"])
        self.result_vars["tiempo"].set(f"{run_result['elapsed']:.3f} s")
        self.result_vars["solver_modelo"].set(f"{run_result['model_used']} / {run_result['solver']}")

        if run_result["status"] not in ("optimo", "factible (optimalidad no confirmada)"):
            self.result_vars["polarizacion"].set("—")
            self.result_vars["mediana"].set("—")
            self.result_vars["costo_usado"].set("—")
            self.result_vars["movimientos_usados"].set("—")
            self.result_vars["personas_movidas"].set("—")
            return

        try:
            solution = minizinc_runner.parse_solution(run_result["raw_output"])
            metrics = minizinc_runner.compute_metrics(data, solution)
        except Exception as exc:
            messagebox.showwarning(
                "Aviso", f"El modelo terminó ({run_result['status']}) pero no se pudo interpretar la solución: {exc}"
            )
            return

        self.result_vars["polarizacion"].set(f"{solution.get('polarizacion', '—')}")
        self.result_vars["mediana"].set(f"{solution.get('mediana', '—')}")
        self.result_vars["costo_usado"].set(f"{metrics['costo_usado']} / {data['ct']}")
        self.result_vars["movimientos_usados"].set(f"{metrics['movimientos_usados']} / {data['max_movs']}")
        self.result_vars["personas_movidas"].set(str(metrics["personas_movidas"]))

        poblacion_final = solution.get("poblacion_final", [])
        if poblacion_final and isinstance(poblacion_final[0], list):
            poblacion_final = poblacion_final[0]
        for i, personas in enumerate(poblacion_final):
            self.dist_tree.insert("", "end", values=(f"Opinión {i + 1}", personas))

        for origen, destino, cantidad in metrics["movimientos"]:
            self.moves_tree.insert("", "end", values=(f"Opinión {origen}", f"Opinión {destino}", cantidad))
        if not metrics["movimientos"]:
            self.moves_tree.insert("", "end", values=("—", "—", "sin movimientos"))
