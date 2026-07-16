# Modelo Matemático Formal — Problema MinPol

## 1. Conjuntos e índices

- $I = J = \{1, \dots, m\}$: conjunto de opiniones posibles.
- $i, j, k$: índices sobre opiniones, $i, j, k \in \{1, \dots, m\}$.
- Se asume que las opiniones vienen ordenadas por su valor ideológico: $v_1 < v_2 < \dots < v_m$.

## 2. Parámetros (datos de entrada)

| Símbolo | Significado | Dominio |
|---|---|---|
| $n$ | número total de personas | $\mathbb{N}$ |
| $m$ | número de opiniones posibles | $\mathbb{N}$ |
| $p_i$ | personas con opinión inicial $i$ | $0..n$ |
| $v_i$ | valor ideológico de la opinión $i$ | $[0,1]$ |
| $c_{i,j}$ | costo base de mover 1 persona de $i$ a $j$ | $\mathbb{R}^+$ |
| $ce_j$ | costo extra por persona que llega a $j$, si $j$ estaba vacía | $\mathbb{R}^+$ |
| $ct$ | costo total máximo permitido | $\mathbb{R}^+$ |
| $MaxMovs$ | máximo de movimientos ponderados por distancia de índices permitidos | $\mathbb{R}^+$ |
| $I_j$ | constante derivada: $I_j = 1$ si $p_j = 0$, si no $I_j = 0$ | $\{0,1\}$ |

> **Nota:** $I_j$ no es una variable de decisión ni requiere Big-M: se calcula directamente de la entrada, antes de resolver el modelo, ya que depende únicamente de si $p_j$ (dato inicial) es cero o no.

## 3. Variables de decisión

- $x_{i,j} \in \mathbb{Z}_{\geq 0}$, para $i \neq j$: número de personas movidas de la opinión $i$ a la opinión $j$.
- $p'_i \in \mathbb{Z}_{\geq 0}$: población final en la opinión $i$ (variable auxiliar derivada de los $x_{i,j}$).

## 4. Restricciones estructurales

**(R1) Conservación de personas por opinión de origen:**
$$\sum_{j \neq i} x_{i,j} \leq p_i \qquad \forall i \in I$$

**(R2) Población final:**
$$p'_i = p_i - \sum_{j \neq i} x_{i,j} + \sum_{k \neq i} x_{k,i} \qquad \forall i \in I$$

**(R3) Conservación total de la población (implícita, pero útil como chequeo):**
$$\sum_{i} p'_i = n$$

**(R4) Límite de movimientos, ponderados por la distancia entre índices de opinión:**
$$\sum_{i \neq j} |i-j| \cdot x_{i,j} \leq MaxMovs$$

**(R5) Costo total permitido** (lineal, ya que $I_j$ es una constante conocida de antemano):
$$\sum_{i \neq j} \left[ c_{i,j}\left(1 + \frac{p_i}{n}\right) + ce_j \cdot I_j \right] x_{i,j} \leq ct$$

## 5. Linealización de la mediana ponderada

La mediana se calcula sobre la población **final** $p'$, ordenada según los valores $v_1 < \dots < v_m$ (que ya vienen ordenados por construcción).

**Población acumulada hasta la opinión $k$:**
$$S_k = \sum_{i=1}^{k} p'_i \qquad \forall k \in \{1,\dots,m\}$$

**Variables binarias auxiliares** $e_k \in \{0,1\}$, indicando si la acumulada hasta $k$ ya alcanzó al menos la mitad de la población:

$$2S_k - n \geq -M(1-e_k) \qquad \forall k$$
$$2S_k \leq n - 1 + M \cdot e_k \qquad \forall k$$
$$e_k \leq e_{k+1} \qquad \forall k < m$$

donde $M$ es una constante suficientemente grande (por ejemplo $M = 2n$).

**Convención de desempate:** si $2S_k = n$ exactamente, se fuerza $e_k = 1$ mediante la segunda desigualdad. Esto define la mediana como una **opinión discreta** (la primera $v_k$ donde la acumulada alcanza el 50%), no como un valor interpolado entre dos opiniones.

**Variable de transición** (marca el índice exacto donde ocurre el cambio de 0 a 1 en $e_k$):
$$d_k = e_k - e_{k-1} \qquad (e_0 := 0), \qquad d_k \in \{0,1\}$$

**Mediana como expresión lineal** (válida porque $v_k$ son constantes conocidas):
$$mediana(p', v) = \sum_{k=1}^{m} d_k \cdot v_k$$

## 6. Linealización de la polarización

La polarización que se desea minimizar es:

$$\sum_{i=1}^{m} p'_i \cdot |v_i - mediana(p',v)|$$

Como la mediana se selecciona entre los valores discretos $v_k$, usando las variables binarias $d_k$, se define primero una matriz constante de distancias ideológicas:

$$D_{i,k} = |v_i - v_k| \qquad \forall i,k \in \{1,\dots,m\}$$

Esta matriz no contiene variables de decisión, porque los valores $v_i$ y $v_k$ son parámetros de entrada.

Para evitar el producto directo entre $p'_i$ y $d_k$, se introduce la variable auxiliar:

$$w_{i,k} \in \mathbb{Z}_{\geq 0} \qquad \forall i,k \in \{1,\dots,m\}$$

donde:

$$w_{i,k} =
\begin{cases}
p'_i & \text{si la mediana es la opinión } k \; (d_k = 1)\\
0 & \text{si la mediana no es la opinión } k \; (d_k = 0)
\end{cases}$$

Esta relación se modela linealmente mediante:

$$w_{i,k} \leq p'_i \qquad \forall i,k$$

$$w_{i,k} \leq n d_k \qquad \forall i,k$$

$$w_{i,k} \geq p'_i - n(1-d_k) \qquad \forall i,k$$

$$w_{i,k} \geq 0 \qquad \forall i,k$$

Estas restricciones son exactas porque $d_k$ es binaria y $0 \leq p'_i \leq n$.

## 7. Manejo del costo extra condicional

A diferencia de lo que podría parecer a primera vista, **no se necesita una formulación Big-M** para el costo extra $ce_j$. La condición "$j$ estaba vacía inicialmente" depende únicamente del parámetro de entrada $p_j$, **no** de ninguna variable de decisión. Por lo tanto:

$$I_j = \begin{cases} 1 & \text{si } p_j = 0 \\ 0 & \text{si } p_j > 0 \end{cases}$$

se calcula **antes** de resolver el modelo, como constante, y se incorpora directamente en la restricción de costo (R5) y en la función objetivo si aplica. Esto simplifica considerablemente la formulación frente a un caso donde la condición dependiera de decisiones del solver.

## 8. Función objetivo

Con la linealización anterior, la función objetivo queda:

$$\min \; \sum_{i=1}^{m} \sum_{k=1}^{m} D_{i,k} \cdot w_{i,k}$$

Esta expresión es equivalente a minimizar:

$$\sum_{i=1}^{m} p'_i \cdot |v_i - mediana(p',v)|$$

pero evita productos entre variables de decisión. Por lo tanto, el modelo queda formulado como un problema de programación entera mixta lineal.

El modelo completo queda sujeto a las restricciones (R1)–(R5), las restricciones de identificación de la mediana (sección 5) y las restricciones de linealización de la polarización (sección 6), con:

$$x_{i,j} \in \mathbb{Z}_{\geq 0}, \quad p'_i \in \mathbb{Z}_{\geq 0}, \quad e_k,d_k \in \{0,1\}, \quad w_{i,k} \in \mathbb{Z}_{\geq 0}$$

---

## 9. Validación con la instancia de ejemplo (n=20, m=5)

**Datos:** $p = [12,4,0,4,0]$, $v = [0, 0.25, 0.5, 0.75, 1]$, $ct=20$, $MaxMovs=18$, $I = [0,0,1,0,1]$ (ya que $p_3=p_5=0$).

**Solución óptima manual a validar:** mover $4$ personas de $2\to1$, $2$ personas de $4\to1$, $2$ personas de $4\to2$.

**(R1) Conservación:**
- $x_{2,1}=4 \leq p_2=4$ 
- $x_{4,1}+x_{4,2}=2+2=4 \leq p_4=4$  

**(R2) Población final:**
$$p' = [12+4+2,\; 4-4+2,\; 0,\; 4-2-2,\; 0] = [18, 2, 0, 0, 0]$$
Coincide con la distribución final obtenida manualmente.  

**(R4) Movimientos ponderados por distancia:**
$$|2-1|\cdot4 + |4-1|\cdot2 + |4-2|\cdot2 = 4+6+4 = 14 \leq MaxMovs=18 \quad  $$
Coincide exactamente con el valor manual de "Movimientos totales = 14".

**(R5) Costo total:**
Como nadie se mueve hacia las opiniones 3 o 5 (las vacías), el término $ce_j \cdot I_j$ no se activa:
$$1\cdot(1+\tfrac{4}{20})\cdot4 + 4\cdot(1+\tfrac{4}{20})\cdot2 + 2\cdot(1+\tfrac{4}{20})\cdot2 = 4.8+9.6+4.8 = 19.2 \leq ct=20 \quad  $$
Coincide exactamente con el costo manual de $19.2$.

**Mediana:**
$$S_1 = 18, \quad 2S_1 = 36 \geq n = 20 \Rightarrow e_1=1 \Rightarrow d_1=1,\ d_k=0\ (k>1)$$
$$mediana(p',v) = v_1 = 0$$

**Polarización (función objetivo):**
$$18\cdot|0-0| + 2\cdot|0.25-0| + 0 + 0 + 0 = 0.5$$

**Resultado:** el modelo reproduce exactamente:
- Distribución final $[18, 2, 0, 0, 0]$  
- Costo total $19.2$  
- Movimientos ponderados $14$  
- Polarización óptima $0.5$  

---

## 10. Convenciones fijadas para evitar ambigüedad

1. La mediana se define como la **opinión discreta** donde la población acumulada alcanza por primera vez el 50% del total, no como un valor interpolado.
2. En caso de empate exacto (la acumulada cae justo en $n/2$), se toma la primera opinión donde esto ocurre (convención de "mediana inferior").
3. El costo extra $ce_j$ se activa **por cada persona** que llega a una opinión $j$ inicialmente vacía, no una única vez por uso de la celda destino.
4. La condición de "opinión vacía" depende exclusivamente del dato de entrada $p_j$, y se trata como constante — no requiere Big-M.
5. La restricción de $MaxMovs$ se mide como $\sum |i-j| \cdot x_{i,j}$ (personas movidas ponderadas por la distancia de índices entre opinión origen y destino), confirmado con el equipo.
