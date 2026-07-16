#!/usr/bin/env python3
from __future__ import annotations

import ast
import csv
import json
import math
import os
import re
import subprocess
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MINIZINC = Path("/Applications/MiniZincIDE.app/Contents/Resources/minizinc")
MODEL = ROOT / "Minizinc.mzn"
SOLVER = os.environ.get("MINIZINC_SOLVER", "highs")
RESULTS_DIR = ROOT / "Resultados"
OWN_OUT_DIR = RESULTS_DIR / "salidas"
BATTERY_OUT_DIR = RESULTS_DIR / "salidas_bateria"
OWN_CSV = RESULTS_DIR / "resultados_pruebas.csv"
BATTERY_CSV = RESULTS_DIR / "resultados_bateria_pruebas.csv"
EXPECTED_CSV = RESULTS_DIR / "Bateria_Pruebas_Solucion.csv"
NOTEBOOK_PATH = RESULTS_DIR / "analisis_pruebas.ipynb"
GRAFICOS_DIR = RESULTS_DIR / "graficos"
OWN_TIMEOUT_SECONDS = 20
BATTERY_TIMEOUT_SECONDS = 120
TOLERANCE = 1e-2

OWN_INSTANCES = [
    ("base_enunciado", ROOT / "DatosProyecto.dzn"),
    ("instancia_01_facil", ROOT / "MisInstancias" / "dzn" / "instancia_01_facil.dzn"),
    ("instancia_02_presupuesto_bajo", ROOT / "MisInstancias" / "dzn" / "instancia_02_presupuesto_bajo.dzn"),
    ("instancia_03_opiniones_vacias", ROOT / "MisInstancias" / "dzn" / "instancia_03_opiniones_vacias.dzn"),
    ("instancia_04_extremos", ROOT / "MisInstancias" / "dzn" / "instancia_04_extremos.dzn"),
    ("instancia_05_grande", ROOT / "MisInstancias" / "dzn" / "instancia_05_grande.dzn"),
]


def strip_comments(text: str) -> str:
    return "\n".join(line.split("%", 1)[0] for line in text.splitlines())


def parse_array(text: str, name: str, cast):
    match = re.search(rf"\b{name}\s*=\s*\[([^\]]*)\]\s*;", text, re.S)
    if not match:
        raise ValueError(f"No se encontro el arreglo {name}")
    return [cast(value.strip()) for value in match.group(1).split(",") if value.strip()]


def parse_scalar(text: str, name: str, cast):
    match = re.search(rf"\b{name}\s*=\s*([^;]+)\s*;", text)
    if not match:
        raise ValueError(f"No se encontro el parametro {name}")
    return cast(match.group(1).strip())


def parse_matrix(text: str, m: int):
    match = re.search(r"\bc\s*=\s*array2d\([^,]+,\s*[^,]+,\s*\[([^\]]*)\]\s*\)\s*;", text, re.S)
    if not match:
        raise ValueError("No se encontro la matriz c")
    flat = [float(value.strip()) for value in match.group(1).split(",") if value.strip()]
    if len(flat) != m * m:
        raise ValueError(f"La matriz c tiene {len(flat)} valores y deberia tener {m * m}")
    return [flat[row * m : (row + 1) * m] for row in range(m)]


def load_instance(path: Path, strict_population: bool):
    text = strip_comments(path.read_text())
    n = parse_scalar(text, "n", int)
    m = parse_scalar(text, "m", int)
    p = parse_array(text, "p", int)
    v = parse_array(text, "v", float)
    ce = parse_array(text, "ce", float)
    c = parse_matrix(text, m)
    ct = parse_scalar(text, "ct", float)
    max_movs = parse_scalar(text, "MaxMovs", int)
    warnings = []

    if len(p) != m or len(v) != m or len(ce) != m:
        raise ValueError(f"{path.name}: algun arreglo no tiene longitud m={m}")
    if sum(p) != n:
        message = f"sum(p)={sum(p)} distinto de n={n}"
        if strict_population:
            raise ValueError(f"{path.name}: {message}")
        warnings.append(message)
    for idx in range(m):
        if abs(c[idx][idx]) > 1e-9:
            raise ValueError(f"{path.name}: c[{idx + 1},{idx + 1}] debe ser 0")

    return {
        "n": n,
        "m": m,
        "p": p,
        "v": v,
        "ce": ce,
        "c": c,
        "ct": ct,
        "MaxMovs": max_movs,
        "advertencias_datos": "; ".join(warnings),
    }


def parse_minizinc_output(output: str):
    last = {}
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("x = "):
            last["x"] = ast.literal_eval(line.split("=", 1)[1].strip())
        elif line.startswith("poblacion_final = "):
            last["poblacion_final"] = ast.literal_eval(line.split("=", 1)[1].strip())
        elif line.startswith("mediana = "):
            last["mediana"] = float(line.split("=", 1)[1].strip())
        elif line.startswith("polarizacion = "):
            last["polarizacion"] = float(line.split("=", 1)[1].strip())
    if not {"x", "poblacion_final", "mediana", "polarizacion"}.issubset(last):
        raise ValueError("No se pudo interpretar una solucion completa de MiniZinc")
    return last


def metrics(data, solution):
    m = data["m"]
    p = data["p"]
    c = data["c"]
    ce = data["ce"]
    n = data["n"]
    initially_empty = [1 if value == 0 else 0 for value in p]
    x = solution["x"]

    people_moved = 0
    weighted_moves = 0
    total_cost = 0.0
    movements = []

    for i in range(m):
        for j in range(m):
            amount = int(round(x[i * m + j]))
            if i == j or amount == 0:
                continue
            people_moved += amount
            weighted_moves += amount * abs((j + 1) - (i + 1))
            unit_cost = c[i][j] * (1.0 + p[i] / n) + ce[j] * initially_empty[j]
            total_cost += amount * unit_cost
            movements.append(f"{i + 1}->{j + 1}: {amount}")

    return {
        "personas_movidas": people_moved,
        "movimientos_usados": weighted_moves,
        "costo_usado": round(total_cost, 6),
        "porcentaje_presupuesto": round(100 * total_cost / data["ct"], 2) if data["ct"] else 0.0,
        "porcentaje_movimientos": round(100 * weighted_moves / data["MaxMovs"], 2) if data["MaxMovs"] else 0.0,
        "movimientos_realizados": "; ".join(movements) if movements else "sin movimientos",
    }


def load_expected_values():
    expected = {}
    if not EXPECTED_CSV.exists():
        return expected
    with EXPECTED_CSV.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            value = row["Valor Solución"].replace(",", ".")
            expected[row["Prueba"]] = float(value)
    return expected


def run_minizinc(instance_path: Path, out_path: Path, timeout_seconds: int):
    start = time.perf_counter()
    try:
        completed = subprocess.run(
            [str(MINIZINC), "--solver", SOLVER, "--time-limit", str(timeout_seconds * 1000), str(MODEL), str(instance_path)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds + 3,
        )
    except subprocess.TimeoutExpired as exc:
        elapsed = time.perf_counter() - start
        partial_output = (exc.stdout or "") + (exc.stderr or "")
        out_path.write_text(partial_output + f"\nTIMEOUT: mas de {timeout_seconds} segundos.\n")
        return "timeout", elapsed, partial_output

    elapsed = time.perf_counter() - start
    full_output = completed.stdout + completed.stderr
    out_path.write_text(full_output)

    if "=====UNSATISFIABLE=====" in full_output:
        return "infeasible", elapsed, full_output
    if completed.returncode != 0:
        return "error", elapsed, full_output
    if "==========" in completed.stdout:
        return "optimo", elapsed, full_output
    if "----------" in completed.stdout:
        return "factible/no_confirmado", elapsed, full_output
    return "sin_solucion_parseable", elapsed, full_output


def build_base_row(name, instance_path, data, status, elapsed, output, timeout_seconds: int):
    row = {
        "instancia": name,
        "archivo": str(instance_path.relative_to(ROOT)),
        "n": data.get("n", ""),
        "m": data.get("m", ""),
        "distribucion_inicial": data.get("p", ""),
        "ct": data.get("ct", ""),
        "MaxMovs": data.get("MaxMovs", ""),
        "estado_solver": status,
        "polarizacion": "",
        "mediana": "",
        "poblacion_final": "",
        "movimientos_realizados": "",
        "costo_usado": "",
        "movimientos_usados": "",
        "personas_movidas": "",
        "porcentaje_presupuesto": "",
        "porcentaje_movimientos": "",
        "tiempo_segundos": round(elapsed, 4),
        "observaciones": data.get("advertencias_datos", ""),
    }
    if status == "timeout":
        row["observaciones"] = (row["observaciones"] + "; " if row["observaciones"] else "") + f"No termino dentro de {timeout_seconds} segundos."
    elif status in {"error", "sin_solucion_parseable"}:
        row["observaciones"] = (row["observaciones"] + "; " if row["observaciones"] else "") + output.strip().replace("\n", " ")[:300]
    elif status == "infeasible":
        row["observaciones"] = (row["observaciones"] + "; " if row["observaciones"] else "") + "MiniZinc reporto instancia infactible."
    return row


def run_group(instances, out_dir: Path, strict_population: bool, timeout_seconds: int):
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, instance_path in instances:
        print(f"Ejecutando {name}...", flush=True)
        try:
            data = load_instance(instance_path, strict_population=strict_population)
        except Exception as exc:
            rows.append({
                "instancia": name,
                "archivo": str(instance_path.relative_to(ROOT)),
                "estado_solver": "datos_invalidos",
                "tiempo_segundos": 0.0,
                "observaciones": str(exc),
            })
            print(f"  datos_invalidos: {exc}", flush=True)
            continue

        out_path = out_dir / f"{name}.out"
        status, elapsed, output = run_minizinc(instance_path, out_path, timeout_seconds)
        row = build_base_row(name, instance_path, data, status, elapsed, output, timeout_seconds)

        if status in {"optimo", "factible/no_confirmado"}:
            try:
                solution = parse_minizinc_output(output)
                extra = metrics(data, solution)
                row.update({
                    "polarizacion": solution["polarizacion"],
                    "mediana": solution["mediana"],
                    "poblacion_final": solution["poblacion_final"],
                    "movimientos_realizados": extra["movimientos_realizados"],
                    "costo_usado": extra["costo_usado"],
                    "movimientos_usados": extra["movimientos_usados"],
                    "personas_movidas": extra["personas_movidas"],
                    "porcentaje_presupuesto": extra["porcentaje_presupuesto"],
                    "porcentaje_movimientos": extra["porcentaje_movimientos"],
                })
            except Exception as exc:
                row["estado_solver"] = "sin_solucion_parseable"
                row["observaciones"] = (row["observaciones"] + "; " if row["observaciones"] else "") + str(exc)

        rows.append(row)
        polar = row.get("polarizacion") if row.get("polarizacion") != "" else "-"
        print(f"  {row['estado_solver']} ({elapsed:.2f}s), polarizacion={polar}", flush=True)
    return rows


def battery_instances():
    dzn_dir = ROOT / "BateriaDePruebas" / "dzn"
    paths = sorted(dzn_dir.glob("MinPol*.dzn"), key=lambda path: int(re.search(r"MinPol(\d+)", path.stem).group(1)))
    return [(path.stem, path) for path in paths]


def add_expected_comparison(rows):
    expected = load_expected_values()
    for row in rows:
        key = f"{row['instancia']}.mpl"
        expected_value = expected.get(key)
        row["valor_esperado"] = expected_value if expected_value is not None else ""
        row["diferencia_abs"] = ""
        row["comparacion_esperada"] = ""
        if expected_value is None:
            row["comparacion_esperada"] = "sin_valor_esperado"
            continue
        if row.get("polarizacion") == "":
            row["comparacion_esperada"] = "sin_resultado_modelo"
            continue
        if row.get("estado_solver") != "optimo":
            diff = abs(float(row["polarizacion"]) - expected_value)
            row["diferencia_abs"] = round(diff, 6)
            row["comparacion_esperada"] = "pendiente_optimalidad"
            continue
        diff = abs(float(row["polarizacion"]) - expected_value)
        row["diferencia_abs"] = round(diff, 6)
        row["comparacion_esperada"] = "coincide" if diff <= TOLERANCE else "diferente"
    return rows


def write_csv(path: Path, rows, extra_fields=None):
    base_fields = [
        "instancia",
        "archivo",
        "n",
        "m",
        "distribucion_inicial",
        "ct",
        "MaxMovs",
        "estado_solver",
        "polarizacion",
        "mediana",
        "poblacion_final",
        "movimientos_realizados",
        "costo_usado",
        "movimientos_usados",
        "personas_movidas",
        "porcentaje_presupuesto",
        "porcentaje_movimientos",
        "tiempo_segundos",
        "observaciones",
    ]
    fieldnames = base_fields + (extra_fields or [])
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def numeric_rows(rows, key):
    return [row for row in rows if row.get(key) not in {"", None} and not (isinstance(row.get(key), float) and math.isnan(row.get(key)))]


def conclusion_own_polarization(rows):
    solved = numeric_rows(rows, "polarizacion")
    if not solved:
        return "No hay resultados numericos suficientes para interpretar la polarizacion."
    best = min(solved, key=lambda row: float(row["polarizacion"]))
    worst = max(solved, key=lambda row: float(row["polarizacion"]))
    return f"La menor polarizacion aparece en `{best['instancia']}` ({float(best['polarizacion']):.2f}) y la mayor en `{worst['instancia']}` ({float(worst['polarizacion']):.2f}); esto indica que las instancias con mayor dispersion o restricciones mas fuertes son mas dificiles de despolarizar."


def conclusion_own_time(rows):
    solved = numeric_rows(rows, "tiempo_segundos")
    if not solved:
        return "No hay tiempos suficientes para interpretar el desempeno."
    slow = max(solved, key=lambda row: float(row["tiempo_segundos"]))
    return f"La instancia que mas tarda es `{slow['instancia']}` ({float(slow['tiempo_segundos']):.2f}s), lo que sugiere que la distribucion de la poblacion puede afectar bastante la busqueda aunque `m` no cambie mucho."


def conclusion_battery_status(rows):
    total = len(rows)
    optimal = sum(1 for row in rows if row.get("estado_solver") == "optimo")
    infeasible = sum(1 for row in rows if row.get("estado_solver") == "infeasible")
    timeouts = sum(1 for row in rows if row.get("estado_solver") == "timeout")
    feasible = sum(1 for row in rows if row.get("estado_solver") == "factible/no_confirmado")
    return f"De {total} pruebas de la bateria, {optimal} terminaron con optimo, {feasible} quedaron como factibles sin prueba de optimalidad, {infeasible} resultaron infactibles y {timeouts} llegaron al limite de tiempo configurado."


def conclusion_battery_comparison(rows):
    compared = [row for row in rows if row.get("comparacion_esperada") in {"coincide", "diferente"}]
    if not compared:
        return "No hay pruebas suficientes con valor del modelo y valor esperado para comparar."
    matches = sum(1 for row in compared if row["comparacion_esperada"] == "coincide")
    return f"El modelo coincide con la solucion esperada en {matches} de {len(compared)} pruebas comparables, usando tolerancia de {TOLERANCE}."


def conclusion_battery_error(rows):
    diffs = [row for row in rows if row.get("diferencia_abs") not in {"", None}]
    if not diffs:
        return "No hay diferencias numericas disponibles para interpretar."
    worst = max(diffs, key=lambda row: float(row["diferencia_abs"]))
    if worst.get("estado_solver") != "optimo":
        return f"La mayor diferencia absoluta aparece en `{worst['instancia']}` ({float(worst['diferencia_abs']):.4f}), pero esa prueba no tiene optimalidad confirmada dentro del limite de tiempo; por eso no se interpreta como error definitivo del modelo."
    return f"La mayor diferencia absoluta aparece en `{worst['instancia']}` ({float(worst['diferencia_abs']):.4f}); esta prueba conviene revisarla manualmente si el objetivo es validar exactitud contra la bateria."


def md_cell(text):
    return {"cell_type": "markdown", "metadata": {}, "source": [line + "\n" for line in text.splitlines()]}


def code_cell(text):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [line + "\n" for line in text.splitlines()]}


def create_notebook(own_rows, battery_rows):
    cells = [
        md_cell(
            "# Analisis de pruebas MinPol\n\n"
            "Este notebook consolida los resultados del modelo MiniZinc sobre la instancia base, las cinco instancias propias y la bateria entregada por el profesor.\n\n"
            "Las instancias propias `.dzn` estan en `../MisInstancias/dzn/`; sus versiones `.mpl` estan en `../MisInstancias/`. La bateria convertida esta en `../BateriaDePruebas/dzn/`."
        ),
        code_cell(
            "import pandas as pd\n"
            "import matplotlib.pyplot as plt\n\n"
            "df = pd.read_csv('resultados_pruebas.csv')\n"
            "bateria = pd.read_csv('resultados_bateria_pruebas.csv')"
        ),
        md_cell("## Instancia base e instancias propias"),
        code_cell(
            "cols = ['instancia', 'n', 'm', 'ct', 'MaxMovs', 'estado_solver', 'polarizacion', 'costo_usado', 'movimientos_usados', 'tiempo_segundos']\n"
            "df[cols]"
        ),
        code_cell(
            "ax = df.plot(kind='bar', x='instancia', y='polarizacion', legend=False, figsize=(10, 4), title='Polarizacion: base e instancias propias')\n"
            "ax.set_ylabel('Polarizacion')\n"
            "plt.xticks(rotation=35, ha='right')\n"
            "plt.tight_layout()\n"
            "plt.show()"
        ),
        md_cell("**Conclusion de la grafica:** " + conclusion_own_polarization(own_rows)),
        code_cell(
            "ax = df.plot(kind='bar', x='instancia', y='tiempo_segundos', legend=False, figsize=(10, 4), title='Tiempo de ejecucion: base e instancias propias')\n"
            "ax.set_ylabel('Segundos')\n"
            "plt.xticks(rotation=35, ha='right')\n"
            "plt.tight_layout()\n"
            "plt.show()"
        ),
        md_cell("**Conclusion de la grafica:** " + conclusion_own_time(own_rows)),
        md_cell("## Bateria de pruebas del profesor"),
        code_cell(
            "bateria[['instancia', 'n', 'm', 'estado_solver', 'polarizacion', 'valor_esperado', 'diferencia_abs', 'comparacion_esperada', 'tiempo_segundos', 'observaciones']]"
        ),
        code_cell(
            "ax = bateria['estado_solver'].value_counts().plot(kind='bar', figsize=(8, 4), title='Estado del solver en la bateria del profesor')\n"
            "ax.set_xlabel('Estado')\n"
            "ax.set_ylabel('Cantidad de pruebas')\n"
            "plt.xticks(rotation=20, ha='right')\n"
            "plt.tight_layout()\n"
            "plt.show()"
        ),
        md_cell("**Conclusion de la grafica:** " + conclusion_battery_status(battery_rows)),
        code_cell(
            "comparables = bateria[bateria['comparacion_esperada'].isin(['coincide', 'diferente'])].copy()\n"
            "ax = comparables.plot(x='instancia', y=['polarizacion', 'valor_esperado'], figsize=(12, 4), marker='o', title='Valor obtenido vs valor esperado')\n"
            "ax.set_ylabel('Polarizacion')\n"
            "plt.xticks(rotation=45, ha='right')\n"
            "plt.tight_layout()\n"
            "plt.show()"
        ),
        md_cell("**Conclusion de la grafica:** " + conclusion_battery_comparison(battery_rows)),
        code_cell(
            "errores = bateria[pd.to_numeric(bateria['diferencia_abs'], errors='coerce').notna()].copy()\n"
            "errores['diferencia_abs'] = errores['diferencia_abs'].astype(float)\n"
            "ax = errores.plot(kind='bar', x='instancia', y='diferencia_abs', legend=False, figsize=(12, 4), title='Diferencia absoluta contra solucion esperada')\n"
            "ax.set_ylabel('Diferencia absoluta')\n"
            "plt.xticks(rotation=45, ha='right')\n"
            "plt.tight_layout()\n"
            "plt.show()"
        ),
        md_cell("**Conclusion de la grafica:** " + conclusion_battery_error(battery_rows)),
        code_cell(
            "ax = bateria.plot(kind='bar', x='instancia', y='tiempo_segundos', legend=False, figsize=(12, 4), title='Tiempo de ejecucion en bateria del profesor')\n"
            "ax.set_ylabel('Segundos')\n"
            "plt.xticks(rotation=45, ha='right')\n"
            "plt.tight_layout()\n"
            "plt.show()"
        ),
        md_cell(
            "**Conclusion de la grafica:** Las pruebas con mayor tiempo son las que requieren mas exploracion del solver o llegan al limite configurado; estas instancias sirven para discutir desempeno y no solo calidad de solucion."
        ),
    ]
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "pygments_lexer": "ipython3"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    NOTEBOOK_PATH.write_text(json.dumps(notebook, indent=2, ensure_ascii=False))


def write_svg_bar(path: Path, labels, values, title: str, y_label: str):
    width = 1100
    height = 460
    margin_left = 80
    margin_bottom = 140
    margin_top = 50
    chart_width = width - margin_left - 30
    chart_height = height - margin_top - margin_bottom
    max_value = max(values) if values else 1.0
    max_value = max_value if max_value > 0 else 1.0
    bar_gap = 8
    bar_width = (chart_width - bar_gap * (len(values) - 1)) / max(len(values), 1)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width / 2}" y="28" text-anchor="middle" font-family="Arial" font-size="20" font-weight="700">{title}</text>',
        f'<text x="20" y="{margin_top + chart_height / 2}" transform="rotate(-90 20 {margin_top + chart_height / 2})" text-anchor="middle" font-family="Arial" font-size="13">{y_label}</text>',
        f'<line x1="{margin_left}" y1="{margin_top + chart_height}" x2="{margin_left + chart_width}" y2="{margin_top + chart_height}" stroke="#333"/>',
        f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + chart_height}" stroke="#333"/>',
    ]
    for index, (label, value) in enumerate(zip(labels, values)):
        bar_height = chart_height * value / max_value
        x = margin_left + index * (bar_width + bar_gap)
        y = margin_top + chart_height - bar_height
        parts.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_width:.2f}" height="{bar_height:.2f}" fill="#4f7cac"/>')
        parts.append(f'<text x="{x + bar_width / 2:.2f}" y="{y - 6:.2f}" text-anchor="middle" font-family="Arial" font-size="10">{value:.2f}</text>')
        parts.append(f'<text x="{x + bar_width / 2:.2f}" y="{margin_top + chart_height + 16}" transform="rotate(55 {x + bar_width / 2:.2f} {margin_top + chart_height + 16})" font-family="Arial" font-size="10">{label}</text>')
    parts.append("</svg>")
    path.write_text("\n".join(parts))


def write_svg_status(path: Path, rows):
    counts = {}
    for row in rows:
        counts[row["estado_solver"]] = counts.get(row["estado_solver"], 0) + 1
    write_svg_bar(path, list(counts.keys()), list(counts.values()), "Estado del solver en bateria", "Cantidad")


def try_create_plots(own_rows, battery_rows):
    GRAFICOS_DIR.mkdir(parents=True, exist_ok=True)
    own_solved = numeric_rows(own_rows, "polarizacion")
    write_svg_bar(
        GRAFICOS_DIR / "polarizacion_por_instancia.svg",
        [row["instancia"] for row in own_solved],
        [float(row["polarizacion"]) for row in own_solved],
        "Polarizacion por instancia propia",
        "Polarizacion",
    )
    write_svg_bar(
        GRAFICOS_DIR / "tiempo_por_instancia.svg",
        [row["instancia"] for row in own_rows],
        [float(row["tiempo_segundos"]) for row in own_rows],
        "Tiempo por instancia propia",
        "Segundos",
    )
    write_svg_status(GRAFICOS_DIR / "bateria_estado_solver.svg", battery_rows)

    battery_solved = numeric_rows(battery_rows, "polarizacion")
    write_svg_bar(
        GRAFICOS_DIR / "bateria_polarizacion_obtenida.svg",
        [row["instancia"] for row in battery_solved],
        [float(row["polarizacion"]) for row in battery_solved],
        "Polarizacion obtenida en bateria",
        "Polarizacion",
    )
    diffs = [row for row in battery_rows if row.get("diferencia_abs") not in {"", None}]
    if diffs:
        write_svg_bar(
            GRAFICOS_DIR / "bateria_diferencia_esperada.svg",
            [row["instancia"] for row in diffs],
            [float(row["diferencia_abs"]) for row in diffs],
            "Diferencia absoluta contra esperado",
            "Diferencia",
        )
    write_svg_bar(
        GRAFICOS_DIR / "bateria_tiempo.svg",
        [row["instancia"] for row in battery_rows],
        [float(row["tiempo_segundos"]) for row in battery_rows],
        "Tiempo en bateria del profesor",
        "Segundos",
    )


def main():
    OWN_OUT_DIR.mkdir(parents=True, exist_ok=True)
    BATTERY_OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("== Instancia base e instancias propias ==", flush=True)
    own_rows = run_group(OWN_INSTANCES, OWN_OUT_DIR, strict_population=True, timeout_seconds=OWN_TIMEOUT_SECONDS)
    write_csv(OWN_CSV, own_rows)

    print("== Bateria del profesor ==", flush=True)
    battery_rows = run_group(battery_instances(), BATTERY_OUT_DIR, strict_population=False, timeout_seconds=BATTERY_TIMEOUT_SECONDS)
    battery_rows = add_expected_comparison(battery_rows)
    write_csv(BATTERY_CSV, battery_rows, extra_fields=["valor_esperado", "diferencia_abs", "comparacion_esperada"])

    print(f"Resultados propios escritos en {OWN_CSV.relative_to(ROOT)}")
    print(f"Resultados bateria escritos en {BATTERY_CSV.relative_to(ROOT)}")
    print(f"Salidas propias escritas en {OWN_OUT_DIR.relative_to(ROOT)}")
    print(f"Salidas bateria escritas en {BATTERY_OUT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
