% =========================================================
% MinPol - Modelo genérico de minimización de polarización
% Versión: No Lineal Corregida para Solvers MIP Lineales
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
array[1..m] of int: I = [ if p[j] = 0 then 1 else 0 endif | j in 1..m ];

% Matriz de distancias constantes
array[1..m, 1..m] of float: D = array2d(1..m, 1..m, [ abs(v[i]-v[k]) | i in 1..m, k in 1..m ]);

% ---------- Variables de decisión ----------
array[1..m, 1..m] of var 0..n: x;        % personas movidas de i a j
array[1..m] of var 0..n: pprime;         % población final por opinión

% REEMPLAZO: En lugar de un entero med_idx, usamos un "vector interruptor" binario
array[1..m] of var bool: d;              % d[k] = true si la opinión k es la mediana

% =========================================================
% Restricciones generales de flujo y costos
% =========================================================

constraint forall(i in 1..m)( x[i,i] = 0 );

constraint forall(i in 1..m)(
    sum(j in 1..m where j != i)( x[i,j] ) <= p[i]
);

constraint forall(i in 1..m)(
    pprime[i] = p[i]
               - sum(j in 1..m where j != i)( x[i,j] )
               + sum(k in 1..m where k != i)( x[k,i] )
);

constraint sum(i in 1..m)( pprime[i] ) = n;

constraint sum(i in 1..m, j in 1..m where i != j)( abs(i-j) * x[i,j] ) <= MaxMovs;

constraint
    sum(i in 1..m, j in 1..m where i != j)(
        x[i,j] * ( c[i,j] * (1.0 + int2float(p[i]) / int2float(n)) + ce[j] * int2float(I[j]) )
    ) <= ct;

% =========================================================
% Cálculo de la Mediana mediante el vector binario 'd'
% =========================================================

% 1. Forzamos a que EXACTAMENTE una opinión sea la mediana
constraint sum(k in 1..m)( bool2int(d[k]) ) = 1;

% 2. La opinión elegida como mediana (donde d[k]=1) debe cumplir la regla del 50%
constraint forall(k in 1..m)(
    if d[k] then sum(i in 1..k)( pprime[i] ) >= (n + 1) div 2 else true endif
);
constraint forall(k in 1..m)(
    if d[k] then sum(i in k..m)( pprime[i] ) >= (n + 1) div 2 else true endif
);

% =========================================================
% Función objetivo linealizada mediante condicionales estáticos
% =========================================================
% Multiplicar por d[k] (binaria) mediante condicionales 'if' hace que MiniZinc 
% genere ecuaciones lineales nativas sin romper el solver.
var float: polarizacion = sum(i in 1..m, k in 1..m)(
    if d[k] then int2float(pprime[i]) * D[i,k] else 0.0 endif
);

solve minimize polarizacion;

% =========================================================
% Salida
% =========================================================
output [
  "x = ", show(x), "\n",
  "poblacion_final = ", show(pprime), "\n",
  "mediana = ", show(sum(k in 1..m)(bool2int(d[k]) * v[k])), "\n",
  "mediana_indice = ", show(d), "\n",
  "polarizacion = ", show(polarizacion), "\n"
];