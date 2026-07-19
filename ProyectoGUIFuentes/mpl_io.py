"""Lectura de archivos de entrada .mpl según Sección 3.1 del enunciado.

Formato esperado (líneas, sin comentarios):
  1. n
  2. m
  3. p_1,...,p_m
  4. v_1,...,v_m
  5. ce_1,...,ce_m
  6..6+m-1. m líneas con c_i,1,...,c_i,m
  siguiente. ct
  siguiente. MaxMovs
"""
from __future__ import annotations

from pathlib import Path


def load_mpl(path: Path) -> dict:
    raw_lines = Path(path).read_text(encoding="utf-8").splitlines()
    lines = [line.strip() for line in raw_lines if line.strip() != ""]

    if len(lines) < 5:
        raise ValueError(f"{Path(path).name}: el archivo no tiene suficientes líneas para ser una entrada .mpl válida")

    idx = 0
    try:
        n = int(lines[idx]); idx += 1
        m = int(lines[idx]); idx += 1
        p = [int(x.strip()) for x in lines[idx].split(",")]; idx += 1
        v = [float(x.strip()) for x in lines[idx].split(",")]; idx += 1
        ce = [float(x.strip()) for x in lines[idx].split(",")]; idx += 1

        if len(p) != m or len(v) != m or len(ce) != m:
            raise ValueError(f"p, v o ce no tienen longitud m={m}")

        c = []
        for _ in range(m):
            if idx >= len(lines):
                raise ValueError("faltan filas de la matriz de costos c")
            row = [float(x.strip()) for x in lines[idx].split(",")]
            if len(row) != m:
                raise ValueError(f"una fila de c no tiene {m} valores")
            c.append(row)
            idx += 1

        ct = float(lines[idx]); idx += 1
        max_movs = int(round(float(lines[idx]))); idx += 1
    except (ValueError, IndexError) as exc:
        raise ValueError(f"{Path(path).name}: formato .mpl inválido ({exc})") from exc

    if sum(p) != n:
        raise ValueError(
            f"{Path(path).name}: la suma de p ({sum(p)}) no coincide con n ({n})"
        )

    return {
        "n": n,
        "m": m,
        "p": p,
        "v": v,
        "ce": ce,
        "c": c,
        "ct": ct,
        "max_movs": max_movs,
    }
