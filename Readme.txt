PROYECTO 2 - MinPol

Este archivo describe los entregables incluidos en la carpeta del proyecto y
explica cómo ejecutar la aplicación gráfica y el modelo MiniZinc.

1. DESCRIPCIÓN GENERAL

El proyecto incluye:
- El modelo de optimización en MiniZinc.
- Archivos de datos de ejemplo e instancias propias.
- Una interfaz gráfica en Python para cargar entradas, generar el archivo
  .dzn y ejecutar el modelo.
- Una carpeta con resultados, pruebas y scripts de apoyo.

2. ARCHIVOS Y CARPETAS ENTREGADAS

- `Proyecto.mzn`
  Modelo principal de MiniZinc usado para resolver el problema MinPol.

- `DatosProyecto.dzn`
  Archivo de datos de entrada que usa el modelo. Puede ser generado desde la
  interfaz gráfica o editado manualmente.

- `BateriaDePruebas/`
  Conjunto de instancias de prueba entregadas para validación.
  - `BateriaDePruebas/MinPol*.mpl`: instancias en formato `.mpl`.
  - `BateriaDePruebas/dzn/MinPol*.dzn`: versiones equivalentes en formato
    MiniZinc `.dzn`.

- `MisInstancias/`
  Instancias propias del proyecto.
  - `MisInstancias/*.mpl`: archivos de entrada en formato `.mpl`.
  - `MisInstancias/dzn/*.dzn`: archivos de entrada convertidos a `.dzn`.

- `ProyectoGUIFuentes/`
  Código fuente de la interfaz gráfica.
  - `main.py`: punto de entrada de la aplicación.
  - `gui_app.py`: interfaz Tkinter completa.
  - `minizinc_runner.py`: ejecución del modelo MiniZinc y lectura de resultados.
  - `mpl_io.py`: lectura de archivos `.mpl`.
  - `dzn_io.py`: generación del archivo `.dzn`.
  - `run_gui.bat`: lanzador para Windows.
  - `run_gui.sh`: lanzador para Linux/macOS.
  - `README.md`: documentación propia de la interfaz.

- `Resultados/`
  Carpeta con evidencia de pruebas y análisis.
  - `ejecutar_pruebas.py`: script para ejecutar pruebas.
  - `requirements.txt`: dependencias usadas para análisis y notebooks.
  - `analisis_pruebas.ipynb`: cuaderno de análisis de resultados.
  - `*.csv`: archivos con resultados obtenidos.
  - `.gitignore`: exclusiones de control de versiones.
  - `.venv/`: entorno virtual local usado para el análisis y pruebas.

- `README.md`
  Archivo corto de apoyo que ya existía en la raíz del proyecto.

3. REQUISITOS PARA EJECUTAR

- Python 3.9 o superior.
- Tkinter instalado con Python.
- MiniZinc instalado.
- Un solver disponible en MiniZinc, por ejemplo `gecode`.

Si MiniZinc no queda en la ruta por defecto de Windows, la aplicación también
puede usar la variable de entorno `MINIZINC_BIN` apuntando al ejecutable
`minizinc.exe`.

4. CÓMO EJECUTAR LA APLICACIÓN GRÁFICA

Opción recomendada:

1. Abrir una terminal en la carpeta `ProyectoGUIFuentes`.
2. Ejecutar:

```bash
python main.py
```

Opciones alternativas:

- En Windows, ejecutar `run_gui.bat`.
- En Linux/macOS, ejecutar `run_gui.sh` con permisos de ejecución.

5. CÓMO USAR LA INTERFAZ

1. Cargar una instancia `.mpl` o usar el ejemplo incluido.
2. Verificar o completar los valores de `n`, `m`, `p`, `v`, `ce`, la matriz
   de costos `c`, `ct` y `MaxMovs`.
3. Pulsar `Generar y ejecutar modelo` para crear `DatosProyecto.dzn` y correr
   `Proyecto.mzn` con MiniZinc.
4. Revisar el panel de resultados para ver el estado, la polarización, la
   mediana, el costo, los movimientos y la salida cruda del solver.

6. EJECUCIÓN MANUAL SIN LA GUI

Si se desea trabajar directamente con MiniZinc:

```bash
minizinc Proyecto.mzn DatosProyecto.dzn
```

7. OBSERVACIONES

- La interfaz valida que la suma de `p` sea igual a `n`.
- La diagonal de la matriz `c` se fija en `0.0`.
- Los archivos `.mpl` deben respetar el formato esperado por el proyecto.

