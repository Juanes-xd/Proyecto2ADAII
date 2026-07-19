"""Generación de archivos .dzn (formato de entrada MiniZinc) para MinPol.

Formato de salida acordado con Persona 2 (formato del modelo):

    n = 20;
    m = 5;

    p = [12, 4, 0, 4, 0];

    v = [0.0, 0.25, 0.5, 0.75, 1.0];

    ce = [1.0, 2.0, 1.0, 1.0, 3.0];

    c = array2d(1..5, 1..5, [
      0.0, 2.0, 4.0, 5.0, 7.0,
      ...
    ]);

    ct = 20.0;
    MaxMovs = 18;
"""
from __future__ import annotations

from pathlib import Path


def format_float(value: float) -> str:
    """Formatea un float siempre con al menos un decimal (20 -> '20.0')."""
    val = float(value)
    text = f"{val:.6f}".rstrip("0")
    if text.endswith("."):
        text += "0"
    return text


def build_dzn_text(n: int, m: int, p, v, ce, c, ct: float, max_movs: int) -> str:
    if len(p) != m or len(v) != m or len(ce) != m:
        raise ValueError("p, v y ce deben tener longitud m")
    if len(c) != m or any(len(row) != m for row in c):
        raise ValueError("c debe ser una matriz m x m")

    lines = [
        f"n = {int(n)};",
        f"m = {int(m)};",
        "",
        "p = [" + ", ".join(str(int(x)) for x in p) + "];",
        "",
        "v = [" + ", ".join(format_float(x) for x in v) + "];",
        "",
        "ce = [" + ", ".join(format_float(x) for x in ce) + "];",
        "",
        f"c = array2d(1..{int(m)}, 1..{int(m)}, [",
    ]
    for i, row in enumerate(c):
        row_text = "  " + ", ".join(format_float(x) for x in row)
        if i < m - 1:
            row_text += ","
        lines.append(row_text)
    lines.append("]);")
    lines.append("")
    lines.append(f"ct = {format_float(ct)};")
    lines.append(f"MaxMovs = {int(max_movs)};")
    return "\n".join(lines) + "\n"


def write_dzn(path: Path, n: int, m: int, p, v, ce, c, ct: float, max_movs: int) -> str:
    text = build_dzn_text(n, m, p, v, ce, c, ct, max_movs)
    Path(path).write_text(text, encoding="utf-8")
    return text
