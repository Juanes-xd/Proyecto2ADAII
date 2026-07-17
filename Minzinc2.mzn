% =========================================================
% MinPol - Modelo genérico de minimización de polarización
% Análisis de Algoritmos II - Univalle
% Versión: Función Objetivo NO Lineal (Versión Compacta)
% =========================================================

% ---------- Parámetros de entrada ----------
int: n;                                  % número total de personas
int: m;                                  % número de opiniones posibles
array[1..m] of int: p;                   % distribución inicial de personas por opinión
array[1..m] of float: v;                 % valor ideológico de cada opinión (ordenado ascendente)
array[1..m, 1..m] of float: c;           % costo base de mover 1 persona de i a j
array[1..m] of float: ce;                % costo extra por llegar a una opinión inicialmente vacía
float: ct;                               % costo total máximo permitido
int: MaxMovs;                            % máximo de movimientos ponderados por distancia de índices

% ---------- Constantes derivadas ----------
% ¿La opinión j estaba vacía? No depende de ninguna decisión del modelo.
array[1..m] of int: I = [ if p[j] = 0 then 1 else 0 endif | j in 1..m ];

% ---------- Variables de decisión ----------
array[1..m, 1..m] of var 0..n: x;        % personas movidas de i a j (x[i,i] se fuerza a 0)
array[1..m] of var 0..n: pprime;         % población final por opinión

% ---------- Variable de decisión: Índice de la mediana ----------
var 1..m: med_idx;                       % Variable entera que representa la POSICIÓN (índice) de la mediana

% =========================================================
% Restricciones Generales
% =========================================================

% (R0) No hay movimientos de una opinión a sí misma
constraint forall(i in 1..m)( x[i,i] = 0 );

% (R1) Conservación: no se puede mover más gente de la que hay en la opinión de origen
constraint forall(i in 1..m)(
    sum(j in 1..m where j != i)( x[i,j] ) <= p[i]
);

% (R2) Población final por opinión
constraint forall(i in 1..m)(
    pprime[i] = p[i]
               - sum(j in 1..m where j != i)( x[i,j] )
               + sum(k in 1..m where k != i)( x[k,i] )
);

% (R3) Conservación total de la población (chequeo redundante, pero explícito)
constraint sum(i in 1..m)( pprime[i] ) = n;

% (R4) Límite de movimientos, ponderados por la distancia entre índices de opinión
constraint sum(i in 1..m, j in 1..m where i != j)( abs(i-j) * x[i,j] ) <= MaxMovs;

% (R5) Costo total permitido (I[j] es constante, por lo que la expresión es lineal)
constraint
    sum(i in 1..m, j in 1..m where i != j)(
        x[i,j] * ( c[i,j] * (1.0 + int2float(p[i]) / int2float(n)) + ce[j] * int2float(I[j]) )
    ) <= ct;

% =========================================================
% Definición No Lineal de la Mediana Discreta
% =========================================================

% Obliga a que med_idx sea la posición exacta donde la población acumulada cruza el 50%
% Se evalúa de manera entera mediante divisiones enteras seguras (div 2)
constraint sum(i in 1..med_idx)( pprime[i] ) >= (n + 1) div 2;
constraint sum(i in med_idx..m)( pprime[i] ) >= (n + 1) div 2;

% =========================================================
% Función objetivo (NO Lineal)
% =========================================================
% Rompe la linealidad de dos formas:
% 1. Accede dinámicamente al vector constante 'v' usando una variable de decisión ('med_idx').
% 2. Multiplica de forma directa la variable de población ('pprime') por la función 'abs()'.

var float: polarizacion = sum(i in 1..m)( 
    int2float(pprime[i]) * abs(v[i] - v[med_idx]) 
);

solve minimize polarizacion;

% =========================================================
% Salida
% =========================================================

output [
  "x = ", show(x), "\n",
  "poblacion_final = ", show(pprime), "\n",
  "mediana = ", show(v[med_idx]), "\n",
  "mediana_indice = ", show(med_idx), "\n",
  "polarizacion = ", show(polarizacion), "\n"
];