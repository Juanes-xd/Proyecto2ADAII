#!/usr/bin/env python3
"""Punto de entrada de la interfaz gráfica de MinPol.

Uso:
    python main.py

Requisitos: Python 3.9+ con Tkinter (incluido en la instalación estándar de
Python en Windows y macOS; en Linux puede requerir el paquete python3-tk).
"""
from gui_app import MinPolApp

if __name__ == "__main__":
    app = MinPolApp()
    app.mainloop()
