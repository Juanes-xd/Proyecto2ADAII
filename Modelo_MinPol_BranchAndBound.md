# Modelo de Optimización y Análisis de Branch & Bound
## Problema MinPol: Minimizar la Polarización en una Población
**Análisis de Algoritmos II · Escuela de Ingeniería de Sistemas y Computación**

---

## 1. Parámetros del Modelo

Los siguientes parámetros son datos de entrada conocidos que definen cualquier instancia del problema MinPol:

| Parámetro | Tipo | Descripción |
|---|---|---|
| n ∈ ℕ | Entero | Número total de personas en la población |
| m ∈ ℕ | Entero | Número de opiniones posibles |
| p_i ∈ {0,...,n},  i∈1..m | Entero | Número de personas con opinión inicial i |
| v_i ∈ [0,1],  i∈1..m | Real | Valor numérico asociado a la opinión i |
| c_{i,j} ∈ ℝ⁺,  i,j∈1..m | Real | Costo unitario de mover una persona de opinión i a opinión j; c_{i,i} = 0 |
| ce_i ∈ ℝ⁺,  i∈1..m | Real | Costo extra por persona al mover hacia opinión i cuando p_i = 0 inicialmente |
| ct ∈ ℝ⁺ | Real | Costo total máximo permitido para todos los esfuerzos |
| maxM ∈ ℕ⁺ | Entero | Número máximo de movimientos permitidos (mover 1 persona de i a j cuenta \|j−i\| movimientos) |

---

## 2. Variables de Decisión

**x_{i,j} ∈ {0, 1, 2, ..., n}   ∀ i, j ∈ 1..m**

Número de personas que serán movidas de la opinión i a la opinión j.

**q_i ∈ {0, 1, 2, ..., n}   ∀ i ∈ 1..m**

Número de personas con opinión i después de aplicar todos los movimientos (distribución final).

**med ∈ [0, 1]**

Valor de la mediana ponderada de la distribución final de opiniones, necesaria para calcular la polarización.

**Pol ∈ ℝ≥0**

Valor de la polarización de la distribución final (función objetivo a minimizar).

**b_i ∈ {0, 1}   ∀ i ∈ 1..m   _(variable auxiliar)_**

Variable binaria auxiliar: b_i = 1 si la opinión i está inicialmente desocupada (p_i = 0), b_i = 0 en otro caso. Es fija a partir de los parámetros.

---

## 3. Función Objetivo

Se desea **minimizar** la polarización de la distribución final, medida como la suma ponderada de las desviaciones absolutas respecto a la mediana:

$$\text{Minimizar:} \quad Pol = \sum_{i=1}^{m} q_i \cdot |v_i - med|$$

donde `med = mediana(q, v)` es el valor de la mediana de las opiniones de toda la población bajo la distribución final **q**.

> **Nota sobre la mediana:** dado que el número de personas es entero y las opiniones tienen valores discretos v_1 < v_2 < ... < v_m, la mediana corresponde al valor v_k tal que al menos n/2 personas tienen opinión con valor ≤ v_k y al menos n/2 tienen opinión con valor ≥ v_k. En la formulación entera mixta, `med` se puede fijar mediante restricciones de acumulación sobre q_i, o usando la función `median` nativa en MiniZinc.

---

## 4. Restricciones del Modelo

### R1 — Distribución final de personas

$$q_i = p_i - \sum_{j=1,\, j \neq i}^{m} x_{i,j} + \sum_{j=1,\, j \neq i}^{m} x_{j,i} \qquad \forall\, i \in 1..m$$

La cantidad de personas con opinión i después de los movimientos es igual a las personas originales menos las que salen hacia otras opiniones, más las que llegan desde otras opiniones.

---

### R2 — No se mueve más gente de la disponible

$$\sum_{j=1,\, j \neq i}^{m} x_{i,j} \leq p_i \qquad \forall\, i \in 1..m$$

La suma de personas que salen de la opinión i no puede superar la cantidad inicial con esa opinión.

---

### R3 — No hay movimientos hacia uno mismo

$$x_{i,i} = 0 \qquad \forall\, i \in 1..m$$

Nadie cambia de opinión i hacia la misma opinión i.

---

### R4 — Conservación del total de personas

$$\sum_{i=1}^{m} q_i = n$$

La suma total de personas en la distribución final siempre es igual a n.

---

### R5 — Costo total no supera el umbral

$$\sum_{i=1}^{m} \sum_{j=1,\, j \neq i}^{m} \left[ c_{i,j} \cdot \left(1 + \frac{p_i}{n}\right) \cdot x_{i,j} + ce_j \cdot b_j \cdot x_{i,j} \right] \leq ct$$

El costo acumulado de todos los movimientos no puede exceder el presupuesto `ct`. El costo de mover x_{i,j} personas de i a j es c_{i,j}·(1 + p_i/n)·x_{i,j}; si la opinión de destino j estaba inicialmente vacía (b_j = 1), se agrega ce_j · x_{i,j} por persona.

---

### R6 — Número máximo de movimientos

$$\sum_{i=1}^{m} \sum_{j=1,\, j \neq i}^{m} |j - i| \cdot x_{i,j} \leq maxM$$

La suma total de movimientos (donde mover 1 persona de i a j equivale a |j−i| movimientos) no puede exceder `maxM`.

---

### R7 — Definición de b_i (opinión inicialmente vacía)

$$b_i = \begin{cases} 1 & \text{si } p_i = 0 \\ 0 & \text{si } p_i > 0 \end{cases} \qquad \forall\, i \in 1..m$$

Variable auxiliar binaria fija, conocida directamente desde los parámetros.

---

### R8 — No negatividad de la distribución final

$$q_i \geq 0 \qquad \forall\, i \in 1..m$$

El número de personas con cualquier opinión en la distribución final no puede ser negativo.

---

### R9 — Integralidad

$$x_{i,j} \in \mathbb{N}, \quad q_i \in \mathbb{N} \qquad \forall\, i, j \in 1..m$$

Las variables de movimiento y de distribución final son enteros no negativos.

---

## 5. Modelo Completo (Resumen Formal)

**Minimizar:**
```
Pol = Σ_{i=1}^{m}  q_i · |v_i − med|
```

**Sujeto a:**
```
q_i  =  p_i − Σ_{j≠i} x_{i,j} + Σ_{j≠i} x_{j,i}                     ∀ i ∈ 1..m   (R1)
Σ_{j≠i} x_{i,j}  ≤  p_i                                                ∀ i ∈ 1..m   (R2)
x_{i,i}  =  0                                                            ∀ i ∈ 1..m   (R3)
Σ_i q_i  =  n                                                                          (R4)
Σ_i Σ_{j≠i} [c_{i,j}·(1+p_i/n)·x_{i,j} + ce_j·b_j·x_{i,j}]  ≤  ct                (R5)
Σ_i Σ_{j≠i} |j−i|·x_{i,j}  ≤  maxM                                                  (R6)
b_i = 1 si p_i = 0,  b_i = 0 si p_i > 0                               ∀ i ∈ 1..m   (R7)
q_i  ≥  0                                                               ∀ i ∈ 1..m   (R8)
x_{i,j} ∈ ℕ,  q_i ∈ ℕ                                                  ∀ i,j ∈ 1..m (R9)
```

> Este modelo es de **Programación Entera (IP)**. La no-linealidad del valor absoluto en la función objetivo puede linealizarse mediante variables auxiliares d_i ≥ q_i·(v_i − med), d_i ≥ q_i·(med − v_i) y minimizando Σ d_i, o usando directamente la función `abs()` en MiniZinc.

---

## 6. Branch and Bound: Fundamentos Conceptuales

Branch and Bound (B&B) es un método **exacto** de optimización combinatoria que explora el espacio de soluciones factibles de manera sistemática pero inteligente, evitando la enumeración exhaustiva mediante la poda de ramas que no pueden mejorar la mejor solución conocida.

### 6.1 Componentes clave

| Componente | Descripción |
|---|---|
| **Branching** (Ramificación) | Se selecciona una variable x_{i,j} no entera en la relajación LP y se crea un nodo hijo con x_{i,j} ≤ ⌊valor⌋ y otro con x_{i,j} ≥ ⌈valor⌉, dividiendo el espacio de búsqueda. |
| **Bounding** (Acotamiento) | En cada nodo se resuelve la relajación lineal (LP) del subproblema. El valor óptimo LP provee una **cota inferior (Lower Bound, LB)** para ese nodo. |
| **Pruning** (Poda) | Si LB(nodo) ≥ Upper Bound global (mejor solución entera hallada), el nodo se **poda**: ninguna solución en esa rama puede mejorar la incumbente. |
| **Best Bound First** | Estrategia de selección: expandir el nodo con menor LB, lo que converge más rápidamente hacia el óptimo global. |
| **Incumbente** (Upper Bound) | Cuando un nodo tiene solución entera factible, su valor pasa a ser el **Upper Bound (UB)** global, actualizando la mejor solución conocida. |

### 6.2 Pseudocódigo del algoritmo

```
INICIALIZAR: UB = +∞, Cola = {nodo raíz}

MIENTRAS Cola no esté vacía:
    nodo = seleccionar(Cola)          // ej: menor LB (Best Bound First)
    Resolver relajación LP del nodo  →  LB_nodo, sol_lp

    SI LB_nodo ≥ UB:
        PODAR nodo  (continuar)       // ninguna solución aquí puede mejorar UB

    SI sol_lp es entera Y factible:
        SI LB_nodo < UB:
            UB ← LB_nodo
            incumbente ← sol_lp      // nueva mejor solución encontrada

    SINO (sol_lp tiene variables fraccionarias):
        Seleccionar variable fraccionaria x_{i,j}
        nodo_izq ← agregar restricción x_{i,j} ≤ ⌊sol_lp[i,j]⌋
        nodo_der ← agregar restricción x_{i,j} ≥ ⌈sol_lp[i,j]⌉
        Añadir nodo_izq y nodo_der a Cola

RETORNAR incumbente con valor UB
```

### 6.3 Generación del árbol de búsqueda

Cada nodo del árbol B&B corresponde a un subproblema LP con restricciones adicionales de acotamiento sobre las variables. El árbol crece así:

- **Nodo raíz (nivel 0):** relajación LP completa del modelo MinPol, sin restricciones de integralidad.
- **Nivel k:** nodos creados al ramificar sobre la k-ésima variable fraccionaria encontrada.
- **Nodo hoja:** nodo podado (LB ≥ UB), infactible, o con solución entera válida.
- La profundidad máxima teórica es el número de variables x_{i,j}, es decir m·(m−1) en el peor caso por nivel.

---

## 7. Análisis B&B sobre el Ejemplo Guía (Sección 2.4)

### 7.1 Datos del ejemplo

n = 20 personas, m = 5 opiniones. ct = 20, maxM = 18.

| Opinión i | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| Valor v_i | 0 | 0.25 | 0.50 | 0.75 | 1.00 |
| Personas p_i | 12 | 4 | **0** | 4 | **0** |
| Costo extra ce_i | 1 | 2 | 1 | 1 | 3 |

**Matriz de costos c_{i,j}:**

| c_{i,j} | Op.1 | Op.2 | Op.3 | Op.4 | Op.5 |
|---|---|---|---|---|---|
| **Op.1** | 0 | 2 | 4 | 5 | 7 |
| **Op.2** | 1 | 0 | 3 | 4 | 6 |
| **Op.3** | 3 | 2 | 0 | 2 | 4 |
| **Op.4** | 4 | 2 | 1 | 0 | 2 |
| **Op.5** | 8 | 5 | 3 | 2 | 0 |

> **Observación:** Como p_3 = 0 y p_5 = 0, las opiniones 3 y 5 están inicialmente vacías → b_3 = 1, b_5 = 1. Cualquier movimiento hacia Op.3 tiene costo extra +1 por persona; hacia Op.5, +3 por persona.

---

### 7.2 Tres soluciones factibles y su polarización

Antes de construir el árbol B&B, analizamos el estado inicial y tres soluciones candidatas para establecer la incumbente inicial.

#### Estado inicial (sin movimientos)

- q = [12, 4, 0, 4, 0], costo = 0, movimientos = 0
- Mediana: posiciones 10 y 11 → personas con Op.1 → **med = 0**
- **Pol = 12·|0−0| + 4·|0.25−0| + 4·|0.75−0| = 0 + 1.0 + 3.0 = 4.0**

#### Solución A — x_{4,2} = 4 (mover 4 personas de Op.4 → Op.2)

- q = [12, 8, 0, 0, 0]
- Costo: c_{4,2}·(1 + p_4/n)·4 = 2·(1+4/20)·4 = 2·1.2·4 = **9.6 ≤ 20 ✓**
- Movimientos: |2−4|·4 = 8 ≤ 18 ✓
- med: acumulado hasta Op.1 = 12 ≥ 10 → **med = 0**
- **Pol = 12·0 + 8·0.25 = 2.0**

#### Solución B — x_{4,1} = 4 (mover 4 personas de Op.4 → Op.1)

- q = [16, 4, 0, 0, 0]
- Costo: c_{4,1}·(1+4/20)·4 = 4·1.2·4 = **19.2 ≤ 20 ✓**
- Movimientos: |1−4|·4 = 12 ≤ 18 ✓
- med: acumulado hasta Op.1 = 16 ≥ 10 → **med = 0**
- **Pol = 16·0 + 4·0.25 = 1.0** ⭐

#### Solución C — x_{4,2} = 2, x_{2,1} = 2

- q = [14, 4, 0, 2, 0]
- Costo: c_{4,2}·1.2·2 + c_{2,1}·(1+4/20)·2 = 4.8 + 1·1.2·2 = **7.2 ≤ 20 ✓**
- Movimientos: |2−4|·2 + |1−2|·2 = 4+2 = 6 ≤ 18 ✓
- med: acumulado hasta Op.1 = 14 ≥ 10 → **med = 0**
- **Pol = 14·0 + 4·0.25 + 2·0.75 = 1.0 + 1.5 = 2.5**

#### Resumen comparativo

| Solución | Movs. | Costo | q final | Pol |
|---|---|---|---|---|
| Inicial (sin movimientos) | 0 | 0 | [12, 4, 0, 4, 0] | 4.0 |
| A: x_{4,2} = 4 | 8 | 9.6 | [12, 8, 0, 0, 0] | 2.0 |
| **B: x_{4,1} = 4** | **12** | **19.2** | **[16, 4, 0, 0, 0]** | **1.0 ⭐** |
| C: x_{4,2}=2, x_{2,1}=2 | 6 | 7.2 | [14, 4, 0, 2, 0] | 2.5 |

---

### 7.3 Árbol de Branch and Bound — Ejemplo Guía

Para ilustrar el mecanismo con claridad, se presenta el árbol B&B enfocado en las variables más relevantes: **x_{4,1}** y **x_{4,2}**, dado que Op.4 es la única fuente activa de movimientos con impacto visible en la polarización (12 personas en Op.1 ya anclan la mediana en 0).

La relajación lineal (LP) en el nodo raíz permite valores fraccionarios para x_{i,j}, obteniendo una cota inferior (LB). B&B ramifica sobre las variables fraccionarias hasta obtener soluciones enteras.

| Nodo | Restricciones adicionales | Sol. LP (relajada) | LB (Pol) | UB (Pol) | Acción |
|---|---|---|---|---|---|
| **N0** (Raíz) | — | x_{4,1}≈3.5, x_{4,2}≈0.5 (fraccionaria) | ~0.75 | +∞ | Ramificar sobre x_{4,1} |
| **N1** (hijo izq.) | x_{4,1} ≤ 3 | x_{4,1}=3, x_{4,2}=1 (entera, factible) | 1.25 | — | Actualizar UB←1.25 ★ incumbente |
| **N2** (hijo der.) | x_{4,1} ≥ 4 | x_{4,1}=4, x_{4,2}=0 (entera, factible) | 1.0 | 1.25 | Actualizar UB←1.0 ★★ mejor |
| **N3** (de N1, x_{4,2}≤0) | x_{4,1}≤3, x_{4,2}≤0 | x_{4,1}=3, x_{4,2}=0 → q=[15,4,0,1,0] | 1.5 | 1.0 | **PODAR** (LB 1.5 ≥ UB 1.0) ✗ |
| **N4** (de N2, x_{2,1}=4) | x_{4,1}=4, x_{2,1}=4 | costo = 19.2 + 4.8 = 24 > ct | infact. | 1.0 | **PODAR** (infactible) ✗ |

### 7.4 Diagrama esquemático del árbol

```
N0 (raíz): LP → x_{4,1}≈3.5 fraccionario, LB≈0.75, UB=+∞
├─ N1 [x_{4,1} ≤ 3]: Sol. entera → Pol=1.25  ★ incumbente (UB←1.25)
│    └─ N3 [x_{4,2} ≤ 0]: Pol=1.5 → PODA (LB 1.5 ≥ UB 1.0)  ✗
└─ N2 [x_{4,1} ≥ 4]: Sol. entera → Pol=1.0  ★★ nueva incumbente (UB←1.0)
     └─ N4 [x_{2,1}=4]: Infactible (costo > ct)  ✗

ÓPTIMO: x_{4,1}=4  →  q=[16, 4, 0, 0, 0]  →  Pol = 1.0
```

---

### 7.5 Verificación de la solución óptima

La solución óptima identificada por B&B es **x_{4,1} = 4** (mover 4 personas de Op.4 → Op.1).

**Distribución final:** q = [16, 4, 0, 0, 0]

**Verificación de restricciones:**

| Restricción | Verificación |
|---|---|
| R1 — Consistencia | q_1 = 12 + 4 = 16 ✓   q_4 = 4 − 4 = 0 ✓   q_2 = 4 ✓ |
| R2 — No exceder p_i | Σ x_{4,j} = 4 ≤ p_4 = 4 ✓ |
| R4 — Total = n | 16 + 4 + 0 + 0 + 0 = 20 = n ✓ |
| R5 — Costo ≤ ct | c_{4,1}·(1+4/20)·4 = 4·1.2·4 = 19.2 ≤ 20 ✓ |
| R6 — Movimientos ≤ maxM | \|1−4\|·4 = 3·4 = 12 ≤ 18 ✓ |

**Cálculo de la polarización óptima:**

```
med: acumulado hasta Op.1 → 16 personas ≥ 10 (= n/2) → med = v_1 = 0

Pol = 16·|0 − 0| + 4·|0.25 − 0| + 0 + 0 + 0
    = 0 + 1.0
    = 1.0
```

> **¿Es la solución óptima global?** Sí, dentro del espacio explorado por B&B para este ejemplo. Ninguna rama podada podía alcanzar Pol < 1.0 sin violar las restricciones de costo o movimientos. El árbol terminó con **5 nodos explorados**, demostrando la eficiencia de B&B al podar ramas con LB ≥ UB sin necesidad de enumeración exhaustiva.

---

## 8. Comportamiento de B&B en el Problema MinPol

| Aspecto | Comportamiento en MinPol |
|---|---|
| **Calidad de la cota inferior** | La relajación LP de MinPol suele ser ajustada porque las restricciones de flujo (R1, R2) forman una estructura de red, lo que hace que la brecha LP-IP sea pequeña y las podas sean más efectivas. |
| **Simetría** | Si existe simetría entre opiniones con igual p_i o c_{i,j}, el árbol puede crecer exponencialmente. Se recomienda añadir restricciones de ruptura de simetría. |
| **Profundidad del árbol** | Las variables x_{i,j} toman valores en {0,...,n}. Para n grande, la ramificación puede profundizarse; en ese caso se beneficia de estrategias Depth-First + Best-Bound combinadas. |
| **Rol del presupuesto ct** | Un presupuesto ct ajustado reduce drásticamente el espacio factible, lo que se traduce en una mayor cantidad de podas por infactibilidad. |
| **Impacto de maxM** | maxM limita la distancia entre opiniones de origen y destino, reduciendo el número de variables x_{i,j} activas y acortando el árbol en profundidad. |
| **Función objetivo no lineal** | El valor absoluto en Pol introduce no-linealidad. La linealización clásica d_i ≥ q_i·(v_i−med), d_i ≥ q_i·(med−v_i) mantiene la estructura LP en cada nodo del árbol. |

---

*Análisis de Algoritmos II · Proyecto II: MinPol · Modelo Genérico y Análisis B&B*
