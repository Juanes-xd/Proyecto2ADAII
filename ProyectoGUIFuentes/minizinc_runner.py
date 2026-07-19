"""Ejecución del modelo MiniZinc y parseo de resultados para la GUI de MinPol."""
from __future__ import annotations

import ast
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Nombre final esperado por el enunciado; se incluyen alternativas como
# respaldo mientras se consolida el archivo definitivo del modelo.
MODEL_CANDIDATES = ["Proyecto.mzn", "Minzinc2.mzn", "Minizinc.mzn"]


class MiniZincNotFoundError(RuntimeError):
    pass


class ModelNotFoundError(RuntimeError):
    pass


def find_minizinc_binary() -> str:
    env_bin = os.environ.get("MINIZINC_BIN")
    if env_bin and Path(env_bin).exists():
        return env_bin

    windows_default = Path(r"C:\Program Files\MiniZinc\minizinc.exe")
    if windows_default.exists():
        return str(windows_default)

    which = shutil.which("minizinc")
    if which:
        return which

    raise MiniZincNotFoundError(
        "No se encontró el ejecutable de MiniZinc.\n"
        "Instale MiniZinc (https://www.minizinc.org/) o defina la variable de entorno "
        "MINIZINC_BIN con la ruta completa a minizinc.exe"
    )


def find_model_file() -> Path:
    for name in MODEL_CANDIDATES:
        candidate = ROOT / name
        if candidate.exists():
            return candidate
    raise ModelNotFoundError(
        "No se encontró el modelo Proyecto.mzn en la raíz del proyecto "
        f"({ROOT}). Verifique que el archivo del modelo esté presente."
    )


def list_available_solvers() -> list[str]:
    try:
        minizinc_bin = find_minizinc_binary()
    except MiniZincNotFoundError:
        return ["gecode", "highs", "coin-bc"]
    try:
        completed = subprocess.run(
            [minizinc_bin, "--solvers-json"],
            capture_output=True, text=True, timeout=10,
        )
        data = json.loads(completed.stdout)
        ids = set()
        for entry in data:
            solver_id = entry.get("id", "")
            if solver_id:
                ids.add(solver_id.split(".")[-1])
        return sorted(ids) if ids else ["gecode", "highs", "coin-bc"]
    except Exception:
        return ["gecode", "highs", "coin-bc"]


def parse_solution(output: str) -> dict:
    result: dict = {}
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("x = "):
            result["x"] = ast.literal_eval(line.split("=", 1)[1].strip())
        elif line.startswith("poblacion_final = "):
            result["poblacion_final"] = ast.literal_eval(line.split("=", 1)[1].strip())
        elif line.startswith("mediana = "):
            result["mediana"] = float(line.split("=", 1)[1].strip())
        elif line.startswith("polarizacion = "):
            result["polarizacion"] = float(line.split("=", 1)[1].strip())
    return result


def _flatten_x(x, m: int):
    """Acepta tanto 'x' como lista plana (m*m) o como lista de listas (m x m)."""
    if x and isinstance(x[0], list):
        flat = []
        for row in x:
            flat.extend(row)
        return flat
    return list(x)


def compute_metrics(data: dict, solution: dict) -> dict:
    m = data["m"]
    p = data["p"]
    c = data["c"]
    ce = data["ce"]
    n = data["n"]
    initially_empty = [1 if value == 0 else 0 for value in p]

    x_flat = _flatten_x(solution["x"], m)

    people_moved = 0
    weighted_moves = 0
    total_cost = 0.0
    movements = []

    for i in range(m):
        for j in range(m):
            amount = x_flat[i * m + j]
            amount = int(round(amount))
            if i == j or amount == 0:
                continue
            people_moved += amount
            weighted_moves += amount * abs((j + 1) - (i + 1))
            unit_cost = c[i][j] * (1.0 + p[i] / n) + ce[j] * initially_empty[j]
            total_cost += amount * unit_cost
            movements.append((i + 1, j + 1, amount))

    return {
        "personas_movidas": people_moved,
        "movimientos_usados": weighted_moves,
        "costo_usado": round(total_cost, 4),
        "movimientos": movements,
    }


def run_model(dzn_path: Path, solver: str = "gecode", time_limit_seconds: int = 30) -> dict:
    minizinc_bin = find_minizinc_binary()
    model_path = find_model_file()

    start = time.perf_counter()
    try:
        completed = subprocess.run(
            [
                minizinc_bin,
                "--solver", solver,
                "--time-limit", str(int(time_limit_seconds * 1000)),
                str(model_path),
                str(dzn_path),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=time_limit_seconds + 10,
        )
    except subprocess.TimeoutExpired as exc:
        elapsed = time.perf_counter() - start
        partial = (exc.stdout or "") + (exc.stderr or "")
        return {
            "status": "timeout",
            "elapsed": elapsed,
            "raw_output": partial,
            "model_used": model_path.name,
            "solver": solver,
        }

    elapsed = time.perf_counter() - start
    full_output = completed.stdout + completed.stderr

    if "=====UNSATISFIABLE=====" in full_output:
        status = "infactible"
    elif completed.returncode != 0:
        status = "error"
    elif "==========" in completed.stdout:
        status = "optimo"
    elif "----------" in completed.stdout:
        status = "factible (optimalidad no confirmada)"
    else:
        status = "sin_solucion_parseable"

    return {
        "status": status,
        "elapsed": elapsed,
        "raw_output": full_output,
        "model_used": model_path.name,
        "solver": solver,
    }
