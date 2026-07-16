# Pruebas y analisis de resultados

## 1. Objetivo de las pruebas

El objetivo de esta seccion es evaluar el comportamiento del modelo MiniZinc para el problema MinPol usando tres grupos de datos:

- La instancia base del enunciado.
- Cinco instancias propias generadas por el grupo.
- La bateria de pruebas entregada por el profesor.

Las pruebas buscan verificar que el modelo encuentra soluciones optimas, que respeta las restricciones de costo y movimientos, y que los valores de polarizacion coinciden con las soluciones esperadas cuando estas estan disponibles.

Las ejecuciones se realizaron con el modelo `Minizinc.mzn`, usando archivos `.dzn`. Para las instancias de la bateria del profesor, los archivos originales `.mpl` fueron convertidos previamente a `.dzn`.

## 2. Instancias evaluadas

Primero se evaluaron seis instancias para analizar con detalle el comportamiento del modelo:

| Instancia | Descripcion |
|---|---|
| `base_enunciado` | Instancia original de la seccion 2.4 del proyecto. |
| `instancia_01_facil` | Instancia pequena donde se esperaba una solucion cercana al consenso. |
| `instancia_02_presupuesto_bajo` | Instancia con presupuesto limitado. |
| `instancia_03_opiniones_vacias` | Instancia con opiniones inicialmente vacias y costos extra. |
| `instancia_04_extremos` | Instancia con poblacion concentrada en opiniones extremas. |
| `instancia_05_grande` | Instancia mediana para observar uso de presupuesto y movimientos. |

Adicionalmente, se evaluaron las 30 instancias de la carpeta `BateriaDePruebas`.

## 3. Resultados de la instancia base y las instancias propias

| Instancia | n | m | ct | MaxMovs | Polarizacion | Costo usado | Mov. usados | Personas movidas | Presupuesto usado | Movs. usados | Tiempo (s) | Estado |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| base_enunciado | 20 | 5 | 20.0 | 18 | 0.50 | 19.20 | 14 | 8 | 96.00% | 77.78% | 0.11 | optimo |
| instancia_01_facil | 12 | 4 | 18.0 | 15 | 0.00 | 13.42 | 9 | 9 | 74.54% | 60.00% | 0.11 | optimo |
| instancia_02_presupuesto_bajo | 24 | 5 | 14.0 | 14 | 7.75 | 14.00 | 6 | 4 | 100.00% | 42.86% | 0.13 | optimo |
| instancia_03_opiniones_vacias | 18 | 5 | 18.0 | 16 | 6.00 | 17.33 | 6 | 3 | 96.30% | 37.50% | 0.15 | optimo |
| instancia_04_extremos | 40 | 5 | 28.0 | 30 | 13.75 | 27.55 | 19 | 19 | 98.39% | 63.33% | 0.15 | optimo |
| instancia_05_grande | 28 | 5 | 30.0 | 24 | 4.00 | 29.79 | 21 | 18 | 99.29% | 87.50% | 0.12 | optimo |

**Grafica sugerida para insertar despues de esta tabla:**  
`Resultados/graficos/01_polarizacion_instancias_propias.png`

Esta grafica permite comparar la polarizacion final de cada instancia. Se observa que `instancia_01_facil` alcanza polarizacion `0`, porque el presupuesto y los movimientos disponibles permiten llegar a una configuracion de consenso. En cambio, `instancia_04_extremos` conserva la mayor polarizacion, porque la poblacion inicia muy separada entre extremos y no es posible eliminar completamente esa distancia sin violar las restricciones. Por lo tanto, la polarizacion final depende no solo del tamano de la instancia, sino tambien de la distribucion inicial y de los recursos disponibles.

## 4. Uso del presupuesto

**Grafica sugerida para insertar en esta seccion:**  
`Resultados/graficos/02_porcentaje_presupuesto_usado.png`

El porcentaje de presupuesto usado permite comparar instancias con valores de `ct` diferentes. Se observa que varias instancias usan casi todo el presupuesto disponible: la instancia base usa `96%`, la instancia 2 usa `100%`, la instancia 3 usa `96.30%`, la instancia 4 usa `98.39%` y la instancia 5 usa `99.29%`.

Esto ocurre porque el modelo intenta aprovechar el presupuesto para mover personas hacia configuraciones menos polarizadas. Por lo tanto, el costo total permitido es una restriccion importante en la mayoria de las pruebas. En particular, cuando el presupuesto se consume casi por completo, es razonable pensar que aumentar `ct` podria permitir soluciones con menor polarizacion.

## 5. Uso del limite de movimientos

**Grafica sugerida para insertar en esta seccion:**  
`Resultados/graficos/03_porcentaje_movimientos_usados.png`

El porcentaje de movimientos usados permite revisar si `MaxMovs` fue una restriccion activa. Se observa que no todas las instancias usan el limite de movimientos en la misma proporcion. Por ejemplo, `instancia_02_presupuesto_bajo` usa solo `42.86%` de los movimientos permitidos, aunque consume el `100%` del presupuesto. En cambio, `instancia_05_grande` usa `87.50%` de los movimientos disponibles.

Esto ocurre porque costo y movimientos restringen aspectos distintos de la solucion. Un movimiento puede ser barato pero consumir mucha distancia, o puede ser cercano pero costoso. Por lo tanto, en algunas instancias limita mas el presupuesto, mientras que en otras tambien pesa bastante el limite `MaxMovs`.

## 6. Personas movidas

**Grafica sugerida para insertar en esta seccion:**  
`Resultados/graficos/04_personas_movidas.png`

Esta grafica muestra cuantas personas cambiaron de opinion en cada instancia. Se observa que `instancia_04_extremos` e `instancia_05_grande` mueven 19 y 18 personas respectivamente, mientras que `instancia_03_opiniones_vacias` mueve solo 3.

Esto ocurre porque el modelo no busca mover muchas personas por si mismo, sino mover las personas que permiten reducir la polarizacion respetando costos y movimientos. Por lo tanto, una solucion con mas personas movidas no necesariamente es mejor; lo importante es si esos movimientos acercan la distribucion final a una configuracion menos polarizada.

## 7. Tiempo de ejecucion

**Grafica sugerida para insertar en esta seccion:**  
`Resultados/graficos/05_tiempo_instancias_propias.png`

Los tiempos de ejecucion de las instancias propias son bajos. Se observa que todas las instancias propias se resuelven en menos de un segundo. Esto ocurre porque el modelo actual se esta ejecutando con un solver MIP adecuado para la formulacion lineal. Por lo tanto, para las instancias propias el modelo es practico y permite obtener soluciones optimas rapidamente.

## 8. Bateria de pruebas del profesor

La bateria del profesor contiene 30 instancias. El archivo `Bateria_Pruebas_Solucion.csv` contiene el valor esperado de la funcion objetivo para cada una. Al ejecutar la bateria con el modelo actual se obtuvo:

| Resultado | Cantidad |
|---|---:|
| Optimo encontrado | 28 |
| Infactible | 2 |
| Total | 30 |

De las 28 instancias que llegaron a estado `optimo`, las 28 coincidieron con el valor esperado del profesor usando una tolerancia de `0.01`.

Las instancias `MinPol28` y `MinPol29` fueron reportadas como infactibles. Al revisar sus datos se encontro que ambas declaran `n = 100`, pero la distribucion inicial suma `125`. Por esta razon no se consideran fallos del modelo, sino inconsistencias en los datos de entrada.

**Grafica sugerida para insertar en esta seccion:**  
`Resultados/graficos/06_estado_solver_bateria.png`

Se observa que casi toda la bateria se resuelve de forma optima y solo dos casos aparecen como infactibles. Esto ocurre porque la mayoria de archivos tienen datos consistentes, mientras que `MinPol28` y `MinPol29` violan la condicion basica de que la suma de la poblacion inicial debe ser igual a `n`. Por lo tanto, el comportamiento del solver es coherente con la informacion de entrada.

## 9. Comparacion contra las soluciones esperadas

**Grafica sugerida para insertar en esta seccion:**  
`Resultados/graficos/07_valor_obtenido_vs_esperado.png`

Esta grafica compara el valor de polarizacion obtenido por el modelo contra el valor esperado de la bateria del profesor. Se observa que las curvas coinciden en las instancias comparables. Esto ocurre porque el modelo reproduce los valores optimos entregados como referencia. Por lo tanto, la bateria del profesor valida que la implementacion respeta la funcion objetivo y las restricciones principales del problema.

**Grafica complementaria sugerida:**  
`Resultados/graficos/08_diferencia_absoluta_esperado.png`

La diferencia absoluta contra el valor esperado es cero o practicamente cero en las instancias comparables. Esto ocurre porque las pequenas diferencias que pueden aparecer se deben al redondeo decimal de valores flotantes. Por lo tanto, no hay evidencia de desviaciones relevantes entre el modelo y las soluciones esperadas.

## 10. Tamano del problema y tiempo de ejecucion

**Grafica sugerida para insertar en esta seccion:**  
`Resultados/graficos/09_tamano_vs_tiempo_bateria.png`

Esta grafica relaciona `m^2` con el tiempo de ejecucion. Se usa `m^2` porque la variable principal `x[i,j]` representa movimientos entre pares de opiniones, y por tanto crece aproximadamente con el cuadrado del numero de opiniones.

Se observa que el tiempo no aumenta de forma perfectamente lineal con `m^2`. Esto ocurre porque el tiempo tambien depende de los costos, el presupuesto, la distribucion inicial y el limite de movimientos. Por lo tanto, el tamano estructural del modelo ayuda a explicar la dificultad, pero no es el unico factor que determina el rendimiento.

**Grafica complementaria sugerida:**  
`Resultados/graficos/10_top10_tiempos_bateria.png`

Esta grafica permite identificar las instancias de la bateria que mas tardaron. Se observa que solo algunas concentran los mayores tiempos de ejecucion. Esto ocurre porque ciertas combinaciones de restricciones generan una busqueda mas exigente para demostrar optimalidad. Por lo tanto, para analizar rendimiento conviene revisar casos puntuales y no solo promedios generales.

## 11. Analisis general

En las pruebas se observa que el modelo responde de forma coherente a las restricciones del problema. Cuando el presupuesto y los movimientos disponibles permiten concentrar la poblacion, el modelo puede llegar a polarizacion `0`, como ocurre en `instancia_01_facil`. Cuando las restricciones son mas fuertes o la poblacion inicia mas separada, la polarizacion final es mayor.

Tambien se observa que el presupuesto suele ser una restriccion muy activa. En varias instancias propias el porcentaje de presupuesto usado supera el `95%`. Esto ocurre porque el modelo utiliza el costo disponible para reducir la polarizacion tanto como sea posible. Por lo tanto, el valor de `ct` tiene un impacto directo sobre la calidad de la solucion.

El limite de movimientos tambien influye, aunque no siempre es la restriccion dominante. En algunos casos queda margen de movimientos, pero el presupuesto se agota primero. Por lo tanto, para interpretar una solucion no basta con mirar la polarizacion final; tambien es necesario revisar costo usado, movimientos usados y cantidad de personas movidas.

La bateria del profesor refuerza la validez del modelo: 28 instancias consistentes fueron resueltas hasta optimalidad y todas coincidieron con los valores esperados. Por lo tanto, los resultados no dependen solo de las instancias creadas por el grupo, sino que tambien se sostienen frente a pruebas externas.

## 12. Conclusiones preliminares

- El modelo encuentra soluciones optimas para la instancia base y las cinco instancias propias.
- En la bateria del profesor, las 28 instancias consistentes coinciden con el valor esperado.
- `MinPol28` y `MinPol29` son infactibles porque sus datos no cumplen que la suma de `p` sea igual a `n`.
- El presupuesto disponible suele ser una restriccion clave para reducir la polarizacion.
- El limite de movimientos tambien afecta la solucion, pero no siempre es la restriccion mas fuerte.
- Mover mas personas no garantiza automaticamente menor polarizacion; importa hacia donde se mueven y cuanto cuesta.
- El tiempo de ejecucion depende del tamano del problema y de la estructura de cada instancia.

## 13. Archivos generados

Los datos y resultados de estas pruebas se encuentran en:

- `MisInstancias/`: contiene las cinco instancias propias en formato `.mpl`.
- `MisInstancias/dzn/`: contiene las cinco instancias propias convertidas a formato `.dzn` para MiniZinc.
- `BateriaDePruebas/dzn/`: contiene la bateria del profesor convertida a formato `.dzn`.
- `Resultados/resultados_pruebas.csv`: resultados de la instancia base y las instancias propias.
- `Resultados/resultados_bateria_pruebas.csv`: resultados de la bateria del profesor y comparacion contra el CSV de soluciones.
- `Resultados/analisis_pruebas.ipynb`: notebook usado para construir tablas y graficas.
- `Resultados/graficos/`: graficas generadas desde el notebook.
