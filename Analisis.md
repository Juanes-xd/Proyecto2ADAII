# 1. Modelo Matemático Genérico (MIP)

El problema de Minimizar la Polarización (MinPol) se ha modelado utilizando técnicas de **Programación Entera Mixta (MIP)**. Esta aproximación es indispensable ya que el problema combina variables que representan individuos (las cuales deben adoptar valores estrictamente discretos/enteros) con variables métricas continuas como las distancias ideológicas y la mediana de la población.

## 1.1. Conjuntos e Índices
* $I = \{1, 2, \dots, m\}$: Conjunto de opiniones de origen (posturas iniciales de los ciudadanos).
* $J = \{1, 2, \dots, m\}$: Conjunto de opiniones de destino (posturas finales tras la reubicación).
* Índices: $i \in I$ y $j \in J$.

## 1.2. Parámetros del Modelo
* $n \in \mathbb{N}$: Número total de personas en la población.
* $m \in \mathbb{N}$: Número total de opiniones posibles.
* $p_i \in \mathbb{N} \cup \{0\}$: Población inicial que ostenta la opinión $i$.
* $v_i \in [0, 1]$: Valor ideológico real y normalizado asignado a la opinión $i$.
* $c_{i,j} \in \mathbb{R}^+$: Costo base de trasladar a un individuo desde la opinión $i$ hacia la opinión $j$ (donde $c_{i,i} = 0$).
* $ce_j \in \mathbb{R}^+$: Costo extra incurrido si se trasladan personas hacia la opinión $j$ cuando esta carecía de población inicial ($p_j = 0$).
* $ct \in \mathbb{R}^+$: Presupuesto financiero máximo permitido para la estrategia de intervención.
* $MaxMovs \in \mathbb{N}$: Cantidad máxima global permitida de pasos o movimientos de distancia.

## 1.3. Variables de Decisión
* $x_{i,j} \in \mathbb{N} \cup \{0\}$ (**Entera Pura**): Cantidad de personas trasladadas de la opinión $i$ a la opinión $j$. No se admiten valores fraccionarios debido a la naturaleza discreta de la población.
* $p'_j \in \mathbb{N} \cup \{0\}$ (**Entera Dependiente**): Cantidad final de ciudadanos que adoptan la opinión $j$ después de la reorganización.
* $med \in [0, 1]$ (**Lineal Continua**): Valor real de la mediana ideológica correspondiente a la distribución de la población final.

## 1.4. Función Objetivo
El modelo busca minimizar la dispersión ideológica agregada de la sociedad respecto a su punto central de equilibrio (mediana), formalizándose de la siguiente manera:

$$\min \quad Z = \sum_{j=1}^{m} p'_j \cdot |v_j - med|$$

## 1.5. Restricciones del Sistema

### A. Conservación de Flujo y Población (Técnica Lineal Entera)
Garantiza que ningún ciudadano sea creado o eliminado durante los traslados, ligando la población inicial y los flujos con la población final:
$$\sum_{j=1}^{m} x_{i,j} = p_i \quad \forall i \in I$$
$$p'_j = \sum_{i=1}^{m} x_{i,j} \quad \forall j \in J$$

### B. Cota de Movimientos Geográficos (Técnica Lineal Entera)
Limita el esfuerzo de cambio de opinión agregando la distancia en casillas recorrida por cada individuo en el espectro:
$$\sum_{i=1}^{m} \sum_{j=1}^{m} x_{i,j} \cdot |j - i| \le MaxMovs$$

### C. Control del Presupuesto Económico y Costos Condicionados (Técnica Lineal Mixta)
El costo de transición se ve afectado por la densidad inicial de la celda de origen mediante el factor $(1 + p_i/n)$. Adicionalmente, si el destino $j$ estaba inicialmente deshabitado ($p_j = 0$), se penaliza con el costo extra $ce_j$ por cada individuo asignado a ese nuevo nicho:

$$\sum_{i=1}^{m} \sum_{j=1}^{m} \left[ c_{i,j} \cdot \left(1 + \frac{p_i}{n}\right) \cdot x_{i,j} \right] + \sum_{i=1}^{m} \sum_{j \in J : p_j = 0} \left[ ce_j \cdot x_{i,j} \right] \le ct$$

### D. Restricción de la Mediana
La variable continua $med$ se halla determinando el valor $v_k$ donde la población acumulada de izquierda a derecha (y viceversa) alcanza o supera de forma estricta el umbral crítico de la mitad de la población ($n/2$).

---

# 2. Análisis del Algoritmo Branch & Bound para el Caso de Estudio

El algoritmo **Branch and Bound (Ramificación y Acotación)** resuelve este modelo MIP mediante una exploración inteligente en forma de árbol. En lugar de evaluar de forma exhaustiva los millones de combinaciones enteras posibles, calcula cotas matemáticas mediante la flexibilización de las restricciones y descarta grupos de soluciones mediante mecanismos de poda.

## 2.1. Parámetros de la Instancia de Prueba (Sección 2.4)
* $n = 20, \quad m = 5$
* $p = [12, 4, 0, 4, 0]$
* $v = [0.0, 0.25, 0.5, 0.75, 1.0]$
* Matriz de costos real $C_{i,j}$ (Cuadro 3 del enunciado):
  $$C = \begin{bmatrix}
  0 & 2 & 4 & 5 & 7\\
  1 & 0 & 3 & 4 & 6\\
  3 & 2 & 0 & 2 & 4\\
  4 & 2 & 1 & 0 & 2\\
  8 & 5 & 3 & 2 & 0
  \end{bmatrix}$$
* Costos extras: $ce = [1, 2, 1, 1, 3]$
* $ct = 20, \quad MaxMovs = 18$

**Nota:** Es crucial utilizar la matriz $C$ proporcionada. En particular, el costo de mover de la opinión 4 a la 1 es $c_{4,1} = 4$ (no 3, como podría sugerir la distancia de índices).

## 2.2. Comportamiento Espacial del Árbol de Búsqueda

### Nodo 0: Relajación Lineal (Raíz)
* **Mecanismo:** El solver suspende temporalmente la obligatoriedad de que las variables $x_{i,j}$ sean enteros puros, permitiendo el traslado de fracciones de personas.
* **Resultado:** Halla una cota inferior (LB) que suele ser bastante baja (cercana a 0), pero al detectar variables fraccionarias, el algoritmo inicia la **Ramificación**.

### Exploración de Tres Salidas Diferentes (Factibles)
Para ilustrar el proceso de acotación, se evalúan tres escenarios válidos que satisfacen de forma estricta los límites de $ct \le 20$ y $MaxMovs \le 18$. Todos los costos están calculados con la matriz real.

1. **Salida A: Traslado de 4 personas de la Opinión 4 a la Opinión 1 ($x_{4,1} = 4$)**
   * *Costo:* $c_{4,1} \cdot (1 + p_4/n) \cdot x_{4,1} = 4 \cdot (1 + 4/20) \cdot 4 = 4 \cdot 1.2 \cdot 4 = 19.2 \le 20$.
   * *Movimientos:* $4 \times |1-4| = 12 \le 18$.
   * *Distribución Final:* $[16, 4, 0, 0, 0] \implies \text{Mediana} = 0.0$.
   * *Polarización:* $(16 \times 0) + (4 \times 0.25) = \mathbf{1.0}$.
   * *Efecto en el Árbol:* Al ser una solución entera válida, el solver la registra como la **Cota Superior Global provisional (UB = 1.0)**.

2. **Salida B: Traslado de 4 personas de la Opinión 2 a la Opinión 1 ($x_{2,1} = 4$)**
   * *Costo:* $1 \cdot (1 + 4/20) \cdot 4 = 4.8 \le 20$.
   * *Movimientos:* $4 \times 1 = 4 \le 18$.
   * *Distribución Final:* $[16, 0, 0, 4, 0] \implies \text{Mediana} = 0.0$.
   * *Polarización:* $(16 \times 0) + (4 \times 0.75) = \mathbf{3.0}$.
   * *Efecto en el Árbol:* Dado que $3.0 > UB = 1.0$, el solver ejecuta una **Poda por Cota**. La rama se descarta por subóptima.

3. **Salida C: Traslado de 2 personas de la Opinión 1 a la Opinión 2 ($x_{1,2} = 2$)**
   * *Costo:* $2 \cdot (1 + 12/20) \cdot 2 = 2 \cdot 1.6 \cdot 2 = 6.4 \le 20$.
   * *Movimientos:* $2 \times 1 = 2 \le 18$.
   * *Distribución Final:* $[10, 6, 0, 4, 0] \implies \text{Mediana} = 0.0$.
   * *Polarización:* $(10 \times 0) + (6 \times 0.25) + (4 \times 0.75) = \mathbf{4.5}$.
   * *Efecto en el Árbol:* Se ejecuta de igual forma una **Poda por Cota** al superar el umbral de 1.0.

### Poda por Inviabilidad (Escenarios Alternativos)
Cuando el árbol intenta abrir ramas que trasladen muchas personas hacia la Opinión 3 ($p_3 = 0$) o la Opinión 5 ($p_5 = 0$), se activan los costos fijos extras ($ce_3 = 1$ o $ce_5 = 3$). El algoritmo calcula linealmente que la sumatoria financiera de la rama superará el tope máximo de $ct = 20$. Por ejemplo, mover a la Opinión 5 es extremadamente costoso ($c_{i,5}$ alto + $ce_5$), por lo que el solver corta estos caminos aplicando una **Poda por Inviabilidad**.

## 2.3. Identificación y Descubrimiento de la Solución Óptima Global

Al continuar con el proceso iterativo de ramificación, el solver evalúa la combinación simultánea de movimientos hacia el foco principal de concentración (Opinión 1).

* **Estrategia Óptima:**
  Mover las 4 personas de la opinión 2 a la opinión 1 ($x_{2,1} = 4$), mover 2 personas de la opinión 4 a la opinión 1 ($x_{4,1} = 2$), y mover las 2 personas restantes de la opinión 4 a la opinión 2 ($x_{4,2} = 2$).

* **Verificación de Factibilidad:**
  * *Costo Financiero:*
    * $x_{2,1}$: $1 \cdot 1.2 \cdot 4 = 4.8$
    * $x_{4,1}$: $4 \cdot 1.2 \cdot 2 = 9.6$
    * $x_{4,2}$: $2 \cdot 1.2 \cdot 2 = 4.8$
    * **Costo Total:** $4.8 + 9.6 + 4.8 = 19.2 \le 20 \quad \text{(Válido)}$.
  * *Pasos Totales:*
    * $4 \times |1-2| = 4$
    * $2 \times |1-4| = 6$
    * $2 \times |2-4| = 4$
    * **Movimientos Totales:** $4 + 6 + 4 = 14 \le 18 \quad \text{(Válido)}$.

* **Configuración Social Resultante:**
  * $p'_1 = 12 + 4 + 2 = 18$
  * $p'_2 = 4 - 4 + 2 = 2$
  * $p'_3 = 0$
  * $p'_4 = 4 - 2 - 2 = 0$
  * $p'_5 = 0$
  * **Distribución final:** $[18, 2, 0, 0, 0]$. La mediana es $v_1 = 0.0$.

* **Polarización Mínima Alcanzable:**
  $$Z = 18 \times |0.0 - 0.0| + 2 \times |0.25 - 0.0| = 0 + 0.5 = \mathbf{0.5}$$

* **Demostración de Optimalidad (Poda Global):**
  Para lograr una polarización inferior a $0.5$ (por ejemplo, $0.25$), se necesitaría tener 19 personas en la Opinión 1 y 1 persona en la Opinión 2. Para lograrlo, se deben mover 7 personas desde las opiniones 2 y 4 hacia la 1, y 1 persona desde la opinión 4 hacia la 2. El costo mínimo de esta configuración es:
  * Mover 4 de 2→1: $4.8$
  * Mover 3 de 4→1: $3 \times 4.8 = 14.4$
  * Mover 1 de 4→2: $2.4$
  * **Costo Total:** $4.8 + 14.4 + 2.4 = 21.6 > 20$.
  Para lograr la polarización $0$ (consenso total en Opinión 1), se necesitaría mover 4 de 2→1 y 4 de 4→1 con un costo total de $4.8 + 19.2 = 24.0 > 20$.
  Dado que el presupuesto impide alcanzar estos valores, el solver confirma que **$Z = 0.5$ es la Solución Óptima Absoluta** para esta instancia.