% =========================================================
% MinPol - Modelo genérico de minimización de polarización
% Análisis de Algoritmos II - Univalle
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

% ---------- Constante derivada: ¿la opinión j estaba vacía? ----------
% No depende de ninguna decisión del modelo, se calcula directo del dato de entrada.
array[1..m] of int: I = [ if p[j] = 0 then 1 else 0 endif | j in 1..m ];

% Big-M para la linealización de la mediana (2n es suficiente y numéricamente seguro)
int: BIGM = 2 * n;

% ---------- Variables de decisión ----------
array[1..m, 1..m] of var 0..n: x;        % personas movidas de i a j (x[i,i] se fuerza a 0)
array[1..m] of var 0..n: pprime;         % población final por opinión

% ---------- Variables auxiliares: mediana ----------
array[1..m] of var 0..n: S;              % población acumulada hasta la opinión k
array[1..m] of var bool: e;              % indicador: ¿la acumulada ya alcanzó el 50%?
array[1..m] of var bool: d;              % indicador de transición (marca el índice de la mediana)
var float: mediana;

% ---------- Variables auxiliares: valor absoluto ----------
array[1..m] of var 0.0..1.0: deltaplus;
array[1..m] of var 0.0..1.0: deltaminus;

% =========================================================
% Restricciones
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
% Linealización de la mediana ponderada
% =========================================================

constraint forall(k in 1..m)( S[k] = sum(i in 1..k)( pprime[i] ) );

% e[k] = 1 si la acumulada hasta k ya alcanzó al menos la mitad de la población
constraint forall(k in 1..m)(
    2 * S[k] - n >= -BIGM * (1 - bool2int(e[k]))
);
constraint forall(k in 1..m)(
    2 * S[k] <= n - 1 + BIGM * bool2int(e[k])
);

% e[k] es monótono no decreciente
constraint forall(k in 1..m-1)( e[k] -> e[k+1] );

% d[k] marca la transición exacta (primer k donde e[k] pasa a verdadero)
constraint d[1] = e[1];
constraint forall(k in 2..m)( d[k] = (e[k] /\ not(e[k-1])) );

% Exactamente una opinión es la mediana
constraint sum(k in 1..m)( bool2int(d[k]) ) = 1;

% Mediana como combinación lineal (válida porque v[k] son constantes)
constraint mediana = sum(k in 1..m)( bool2int(d[k]) * v[k] );

% =========================================================
% Linealización del valor absoluto
% =========================================================

constraint forall(i in 1..m)(
    v[i] - mediana = deltaplus[i] - deltaminus[i]
);

% =========================================================
% Función objetivo
% =========================================================

var float: polarizacion = sum(i in 1..m)( int2float(pprime[i]) * (deltaplus[i] + deltaminus[i]) );

solve minimize polarizacion;

% =========================================================
% Salida
% =========================================================

output [
  "x = ", show(x), "\n",
  "poblacion_final = ", show(pprime), "\n",
  "mediana = ", show(mediana), "\n",
  "polarizacion = ", show(polarizacion), "\n"
];
