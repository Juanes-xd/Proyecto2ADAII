# Pruebas y analisis de resultados

## 1. Objetivo de las pruebas

El objetivo de las pruebas fue evaluar el modelo MiniZinc del problema MinPol usando la instancia base del enunciado, cinco instancias propias y la bateria de pruebas entregada por el profesor. Para cada instancia se registro la polarizacion final, el costo usado, los movimientos usados, la cantidad de personas movidas, el tiempo de ejecucion y el estado reportado por el solver.

Las instancias propias permiten analizar casos disenados por el grupo. La bateria del profesor permite validar el modelo contra valores esperados externos.

## 2. Instancias evaluadas

| Instancia | Descripcion |
|---|---|
| `base_enunciado` | Instancia original de la seccion 2.4 del proyecto. |
| `instancia_01_facil` | Instancia pequena donde se esperaba una solucion cercana al consenso. |
| `instancia_02_presupuesto_bajo` | Instancia con presupuesto limitado. |
| `instancia_03_opiniones_vacias` | Instancia con opiniones inicialmente vacias y costos extra. |
| `instancia_04_extremos` | Instancia con poblacion concentrada en opiniones extremas. |
| `instancia_05_grande` | Instancia mediana para observar uso de presupuesto y movimientos. |

Tambien se evaluaron las 30 instancias de `BateriaDePruebas`. Los archivos originales estaban en formato `.mpl` y se convirtieron a `.dzn` para ejecutarlos con MiniZinc.

## 3. Resultados de la instancia base y las instancias propias

| Instancia | n | m | ct | MaxMovs | Polarizacion | Costo usado | Mov. usados | Personas movidas | Presupuesto usado | Movs. usados | Tiempo (s) | Estado |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| base_enunciado | 20 | 5 | 20.0 | 18 | 0.50 | 19.20 | 14 | 8 | 96.00% | 77.78% | 0.11 | optimo |
| instancia_01_facil | 12 | 4 | 18.0 | 15 | 0.00 | 13.42 | 9 | 9 | 74.54% | 60.00% | 0.11 | optimo |
| instancia_02_presupuesto_bajo | 24 | 5 | 14.0 | 14 | 7.75 | 14.00 | 6 | 4 | 100.00% | 42.86% | 0.13 | optimo |
| instancia_03_opiniones_vacias | 18 | 5 | 18.0 | 16 | 6.00 | 17.33 | 6 | 3 | 96.30% | 37.50% | 0.15 | optimo |
| instancia_04_extremos | 40 | 5 | 28.0 | 30 | 13.75 | 27.55 | 19 | 19 | 98.39% | 63.33% | 0.15 | optimo |
| instancia_05_grande | 28 | 5 | 30.0 | 24 | 4.00 | 29.79 | 21 | 18 | 99.29% | 87.50% | 0.12 | optimo |

**Figura 1. Polarizacion final obtenida en la instancia base y las cinco instancias propias.**  
Archivo sugerido: `Resultados/graficos/01_polarizacion_instancias_propias.png`

La menor polarizacion fue `0.00` en `instancia_01_facil`. En esa instancia se movieron 9 personas y se uso el 74.54 % del presupuesto, suficiente para concentrar la poblacion final en una sola opinion. La mayor polarizacion fue `13.75` en `instancia_04_extremos`, donde la poblacion inicial estaba distribuida entre opiniones extremas. Aunque se movieron 19 personas y se uso el 98.39 % del presupuesto, la solucion no pudo eliminar totalmente la distancia ideologica inicial.

## 4. Uso de recursos y comportamiento de las soluciones

**Figura 2. Porcentaje de presupuesto y porcentaje de movimientos utilizados por instancia.**  
Archivo sugerido: `Resultados/graficos/02_recursos_presupuesto_movimientos.png`

En cinco de las seis instancias propias se utilizo mas del 95 % del presupuesto: `base_enunciado`, `instancia_02_presupuesto_bajo`, `instancia_03_opiniones_vacias`, `instancia_04_extremos` e `instancia_05_grande`. La unica excepcion fue `instancia_01_facil`, que alcanzo polarizacion `0.00` usando solo el 74.54 % del presupuesto.

La comparacion entre presupuesto y movimientos muestra que las dos restricciones no actuan igual. En `instancia_02_presupuesto_bajo` se consumio el 100 % del costo permitido, pero solo el 42.86 % de los movimientos. En ese caso, el presupuesto fue la restriccion dominante. En `instancia_05_grande`, en cambio, se uso el 99.29 % del presupuesto y el 87.50 % de los movimientos, por lo que ambas restricciones quedaron bastante ajustadas.

La cantidad de personas movidas tambien cambia bastante entre instancias. `instancia_03_opiniones_vacias` movio solo 3 personas y obtuvo polarizacion `6.00`; `instancia_04_extremos` movio 19 personas y aun asi obtuvo polarizacion `13.75`. Esto muestra que mover mas personas no garantiza una polarizacion menor: importa el costo, la distancia entre opiniones y la posicion final de esas personas respecto a la mediana.

## 5. Validacion con la bateria del profesor

La bateria contiene 30 instancias. Al ejecutarlas con el modelo actual se obtuvo:

| Resultado | Cantidad |
|---|---:|
| Optimo encontrado | 28 |
| Infactible | 2 |
| Total | 30 |

Las 28 instancias que llegaron a estado `optimo` coincidieron con el valor esperado del archivo `Bateria_Pruebas_Solucion.csv`, usando tolerancia de `0.01`.

Las instancias `MinPol28` y `MinPol29` fueron reportadas como infactibles. En ambos casos se encontro la misma inconsistencia: declaran `n = 100`, pero la distribucion inicial suma `125`. Por esa razon no se consideran errores del modelo.

**Figura 3. Estado de las instancias de la bateria del profesor.**  
Archivo sugerido: `Resultados/graficos/03_estado_solver_bateria.png`

La grafica de estados permite ver que el modelo resolvio todas las instancias consistentes de la bateria. Las dos instancias no resueltas corresponden a entradas inconsistentes, no a falta de capacidad del solver para optimizar el modelo.

## 6. Comparacion contra las soluciones esperadas

**Figura 4. Valor obtenido por el modelo frente al valor esperado en la bateria del profesor.**  
Archivo sugerido: `Resultados/graficos/04_valor_obtenido_vs_esperado.png`

En las 28 instancias comparables, el valor obtenido coincide con el valor esperado. En la mayoria de los casos la diferencia absoluta fue `0.000`; en algunos casos aparece una diferencia de `0.001`, atribuible al redondeo de valores decimales. Por ejemplo, `MinPol10` tiene valor esperado `9.686` y el modelo reporta aproximadamente `9.687`, diferencia que queda dentro de la tolerancia definida.

Como todas las diferencias relevantes son nulas o de redondeo, la grafica de diferencia absoluta no es indispensable como figura principal. Puede reemplazarse por una tabla breve si se desea documentar la tolerancia:

| Criterio | Resultado |
|---|---:|
| Instancias comparables | 28 |
| Coincidencias dentro de tolerancia 0.01 | 28 |
| Diferencia maxima observada | 0.001 |

## 7. Tamano de la instancia y tiempo de ejecucion

**Figura 5. Tamano de la instancia frente al tiempo de ejecucion.**  
Archivo sugerido: `Resultados/graficos/05_tamano_vs_tiempo_bateria.png`

Para representar el tamano estructural del modelo se uso $m^2$, porque la variable principal $x_{i,j}$ considera movimientos entre pares de opiniones. A mayor cantidad de opiniones, el numero de posibles movimientos crece de forma cuadratica.

La grafica muestra que el tiempo no depende unicamente de $m^2$. Algunas instancias con mas opiniones se resuelven rapidamente, mientras que otras de tamano similar pueden tardar mas. Esto se debe a que tambien influyen el presupuesto, el limite de movimientos, la distribucion inicial y los costos de traslado. Por eso, para analizar rendimiento no basta con mirar el tamano; tambien hay que revisar la estructura de los datos.

## 8. Analisis general

El modelo resolvio como optimas la instancia base y las cinco instancias propias. En la bateria del profesor resolvio 28 instancias consistentes y en todas coincidio con el valor esperado. Esto valida que la formulacion usada en MiniZinc reproduce correctamente la funcion objetivo y las restricciones del problema.

El presupuesto fue una restriccion fuerte en la mayoria de las instancias propias: cinco de seis usaron mas del 95 % del costo permitido. La instancia mas clara es `instancia_02_presupuesto_bajo`, que uso el 100 % del presupuesto pero solo el 42.86 % de los movimientos. En esa prueba, aumentar `MaxMovs` no necesariamente mejoraria la solucion si el presupuesto se mantiene igual.

El limite de movimientos fue mas relevante en `instancia_05_grande`, donde se uso el 87.50 % de `MaxMovs`. En esa instancia tambien se uso el 99.29 % del presupuesto, por lo que ambas restricciones limitaron la solucion.

Las pruebas tambien muestran que una mayor intervencion no siempre implica menor polarizacion. `instancia_04_extremos` movio 19 personas, pero quedo con polarizacion `13.75`. En cambio, la instancia base movio 8 personas y alcanzo polarizacion `0.50`. La diferencia se explica por la distribucion inicial y por la distancia ideologica de las opiniones involucradas.

## 9. Conclusiones preliminares

- El modelo encuentra soluciones optimas para la instancia base y las cinco instancias propias.
- En la bateria del profesor, las 28 instancias consistentes coinciden con el valor esperado.
- `MinPol28` y `MinPol29` son infactibles porque sus datos no cumplen que la suma de $p_i$ sea igual a $n$.
- En cinco de las seis instancias propias se uso mas del 95 % del presupuesto, por lo que el costo total fue una restriccion dominante.
- El limite de movimientos fue especialmente relevante en `instancia_05_grande`, donde se uso el 87.50 % de `MaxMovs`.
- La cantidad de personas movidas debe interpretarse junto con la polarizacion final: mover mas personas no garantiza una mejor solucion.
- El tiempo de ejecucion depende del tamano del modelo, pero tambien de la estructura de costos, poblacion inicial y restricciones.

## 10. Archivos generados

- `MisInstancias/`: cinco instancias propias en formato `.mpl`.
- `MisInstancias/dzn/`: cinco instancias propias convertidas a `.dzn`.
- `BateriaDePruebas/dzn/`: bateria del profesor convertida a `.dzn`.
- `Resultados/resultados_pruebas.csv`: resultados de la instancia base y las instancias propias.
- `Resultados/resultados_bateria_pruebas.csv`: resultados de la bateria del profesor y comparacion contra soluciones esperadas.
- `Resultados/analisis_pruebas.ipynb`: notebook usado para construir tablas y graficas.
- `Resultados/graficos/`: graficas generadas desde el notebook.
