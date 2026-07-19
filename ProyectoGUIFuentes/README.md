# Interfaz gráfica MinPol

Interfaz de escritorio (Python + Tkinter, sin dependencias externas) para
configurar o leer una entrada del problema MinPol, generar `DatosProyecto.dzn`,
ejecutar el modelo `Proyecto.mzn` con MiniZinc y visualizar la solución.

## Requisitos

- Python 3.9 o superior con Tkinter (incluido por defecto en Windows/macOS;
  en Linux instalar `sudo apt install python3-tk` si falta).
- [MiniZinc](https://www.minizinc.org/) instalado, con al menos un solver
  (Gecode viene incluido en el instalador oficial).
- El archivo del modelo (`Proyecto.mzn`) debe estar en la raíz del proyecto,
  un nivel arriba de esta carpeta. Mientras se consolida ese archivo, la GUI
  también acepta `Minzinc2.mzn` o `Minizinc.mzn` como respaldo automático.

## Ejecución

```bash
cd ProyectoGUIFuentes
python main.py
```

En Windows también se puede hacer doble clic en `run_gui.bat`. En Linux/macOS,
`./run_gui.sh` (dar permisos de ejecución con `chmod +x run_gui.sh` la primera vez).

Si MiniZinc no está en `C:\Program Files\MiniZinc\minizinc.exe` ni en el PATH,
defina la variable de entorno `MINIZINC_BIN` con la ruta al ejecutable antes
de iniciar la GUI.

## Uso

1. **Configurar la entrada a mano**: defina `n`, `m`, luego use "Generar tabla"
   para crear las filas de opiniones (`p`, `v`, `ce`) y la matriz de costos `c`.
   La diagonal de `c` queda fija en `0.0` (no editable), tal como exige el modelo.
2. **O cargar una entrada existente**: botón "Cargar entrada (.mpl)", selecciona
   un archivo con el formato de la Sección 3.1 del enunciado (7 bloques de
   líneas: n, m, p, v, ce, m filas de c, ct, MaxMovs). El formulario se llena
   automáticamente.
3. **Botón "Cargar ejemplo del enunciado"**: precarga la instancia guía de la
   Sección 2.4 (n=20, m=5) para pruebas rápidas o demo en video.
4. **Generar y ejecutar modelo**: valida la entrada, escribe
   `../DatosProyecto.dzn` en la raíz del proyecto, ejecuta
   `minizinc Proyecto.mzn DatosProyecto.dzn` con el solver y límite de tiempo
   elegidos, y muestra en el panel derecho: estado del solver, polarización,
   mediana, costo y movimientos usados frente a los límites, distribución
   final por opinión, tabla de movimientos `i -> j` y la salida cruda de
   MiniZinc (para depuración o mostrar en el video).
5. **Solo generar DatosProyecto.dzn**: útil si solo se quiere inspeccionar el
   archivo generado sin correr el solver.

## Validaciones aplicadas antes de ejecutar

- `sum(p) == n`.
- `p_i >= 0`, `ct >= 0`, `MaxMovs >= 0`.
- La matriz `c` debe ser `m x m`; la diagonal se fuerza a `0.0`.
- Todos los campos numéricos se validan como enteros/reales antes de escribir
  el `.dzn` (errores se muestran en un cuadro de diálogo, sin cerrar la app).

## Archivos de este directorio

| Archivo | Rol |
|---|---|
| `main.py` | Punto de entrada (`python main.py`). |
| `gui_app.py` | Interfaz Tkinter: formulario, botones, panel de resultados. |
| `dzn_io.py` | Construye el texto de `DatosProyecto.dzn` con el formato acordado. |
| `mpl_io.py` | Parser de archivos de entrada `.mpl` (Sección 3.1). |
| `minizinc_runner.py` | Localiza `minizinc`/`Proyecto.mzn`, ejecuta el solver y parsea la salida. |
| `run_gui.bat` / `run_gui.sh` | Lanzadores directos para Windows / Linux-macOS. |

## Formato de `DatosProyecto.dzn` generado

```
n = 20;
m = 5;

p = [12, 4, 0, 4, 0];

v = [0.0, 0.25, 0.5, 0.75, 1.0];

ce = [1.0, 2.0, 1.0, 1.0, 3.0];

c = array2d(1..5, 1..5, [
  0.0, 2.0, 4.0, 5.0, 7.0,
  1.0, 0.0, 3.0, 4.0, 6.0,
  3.0, 2.0, 0.0, 2.0, 4.0,
  4.0, 2.0, 1.0, 0.0, 2.0,
  8.0, 5.0, 3.0, 2.0, 0.0
]);

ct = 20.0;
MaxMovs = 18;
```

Este formato fue acordado con el resto del equipo (autor del modelo) y
coincide con el archivo `DatosProyecto.dzn` ya existente en la raíz del
proyecto.
