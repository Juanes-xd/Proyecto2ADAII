## de curso Proyecto 

# **El Problema de Minimizar la Polarizacion presente en una Poblacion (MinPol)** - Actualizado 

Analisis de Algoritmos II 

Escuela de Ingenierıa de Sistemas y Computacion 

30 de Junio - (actualizado 9 julio) 

## **1. Introduccion** 

El presente proyecto tiene por objeto verificar que los estudiantes han adquirido el siguiente resultado de aprendizaje: 

Construye modelos de optimizacion en terminos de parametros, variables, restricciones y funcion objetivo, a partir de un problema determinado, para explorar soluciones practicas utilizando herramientas computacionales de modelamiento y solvers existentes. 

Para ello, los estudiantes deben demostrar que logran: 

- Utilizar el metodo branch and bound para resolver problemas de programacion binaria, entera y mixta. 

- Usa tecnicas de programacion lineal para modelar/solucionar problemas de programacion lineal en terminos de parametros, variables, restricciones y funcion objetivo. 

- Usa tecnicas de programacion entera para modelar/solucionar problemas de programacion entera en terminos de parametros, variables, restricciones y funcion objetivo. 

- Usa tecnicas de programacion entera mixta para modelar/solucionar problemas de programacion entera mixta en terminos de parametros, variables, restricciones y funcion objetivo. 

- Usa un lenguaje de modelamiento para escribir y probar modelos de programacion lineal, entera y entera mixta. 

Para ello el estudiante: 

- Desarrolla un programa utilizando tecnologıas de programacion adecuadas para resolver en grupo un proyecto de programacion planteado por el profesor. 

1 

- Escribe un informe de proyecto, presentando los aspectos mas relevantes del desarrollo realizado, para que un lector pueda evaluar el proyecto. 

Desarrolla una presentacion digital, con los aspectos mas relevantes del desarrollo realizado, para sustentar el trabajo ante los compa˜neros y el profesor. 

## **2. El Problema de Minimizar la Polarizacion presente en una Poblacion: MinPol** 

## **2.1. Contexto del problema** 

La polarizacion, ası como el extremismo, es un fenomeno que se presenta cada vez de forma mas frecuente en nuestra sociedad, este fenomeno se agudiza cuando las sociedades se tienden a dividir en dos grandes bandos, de tama˜nos similares, donde la opinion de cada bando es totalmente opuesta a la del otro. 

El nivel de polarizacion presente en una sociedad se puede medir de diversas maneras, una forma de hacerlo es considerando el esfuerzo requerido para llevar a toda la poblacion a un consenso. Donde el consenso se refiere a que todas las personas han alcanzando una opinion comun con respecto a un tema. 1 

Entendiendo que un alto nivel de polarizacion, al menos en algunos casos, tiene un potencial efecto corrosivo y perjudicial en el funcionamiento de comunidades, sociedades y democracias, es interesante estudiar estrategias que permitan reducir la polarizacion. Sin embargo, los esfuerzos para reducir la polarizacion tienen un costo que puede ser muy alto, por ende la toma de decisiones que se tomen en pro de reducir la polarizacion constituye un problema bastante relevante y es el tema central de este proyecto. 

En este proyecto, partiendo de las opiniones iniciales de una poblacion, se determinara que esfuerzos se haran para cambiar la opinion de algunos con el fin de alcanzar el menor nivel de polarizacion, entendiendo que los esfuerzos tienen un costo y que este no puede ser mas elevado de un umbral definido. 

## **2.2. El problema** 

El problema de minimizar la polarizacion en una poblacion consiste en decidir que esfuerzos se haran para cambiar la opinion de un grupo de personas y hacia donde, teniendo en cuenta que cada esfuerzo cuesta y que hay recursos limitados, de tal forma que la poblacion termine lo menos polarizada posible. 

En un ejemplo simplificado, imagine que en una poblacion de tama˜no 10, donde tenemos tres posibles opiniones: opinion 1, opinion 2 y opinion 3 ; las opiniones iniciales de la poblacion sobre una propuesta son las siguientes: 

- 8 personas comparten la opinion 1. 

- 0 personas comparten la opinion 2. 

- 2 personas comparten la opinion 3. 

El esfuerzo para mover una persona de una opinion a otra se muestra en la siguiente tabla: 

|Costo esfuerzo|opinion 1|opinion 2|opinion 3|
|---|---|---|---|
|opinion 1|0|3|5|
|opinion 2|2|0|3|
|opinion 3|4|3|0|



> 1La polarizacion es un fenomeno diferente al extremismo, por ejemplo, un grupo de personas que comparta una opinion radical sobre un tema serıa extremista, sin embargo, dicho grupo no estarıa polarizado ya que todos piensan lo mismo. 

2 

Adicionalmente, el costo maximo permitido de los esfuerzos es 9. 

¿Cuales serıan los esfuerzos o acciones que se harıan para lograr minimizar la polarizacion, si las acciones permitidas solo consisten en pasar _x_ personas de una opinion _i_ a una opinion _j_ ? 

En este caso, un esfuerzo podrıa ser el siguiente: mover dos personas de la opinion 3 a la opinion 1. Este esfuerzo, segun la tabla, costarıa en total 8 (ya que serıa el costo individual de mover de _Op_ 3 a _Op_ 1 por dos ya que se mueven dos personas), siendo este costo menor al umbral de 9. Como en este caso se alcanza consenso en la opinion 1, el valor de la polarizacion alcanzado es 0. Por lo tanto mover las opiniones de las dos personas de la opinion 3 a la opinion 1 es una solucion del problema. 

En la realidad y en en este ejercicio, el problema es un poco mas complejo, porque el costo de mover _x_ personas de una opinion _i_ a una opinion _j_ no es tan simple como en este ejemplo. Y el numero de cambios de opinion pueden estar restringidos. 

Por otro lado, ¿que ocurre cuando no se alcanza consenso, porque el esfuerzo para ello es superior al umbral permitido? El objetivo serıa llegar a una configuracion donde la polarizacion sea mınima. Pero, ¿como se mide en ese caso la polarizacion? Para medir la polarizacion en general, incluyendo casos donde no se alcanza consenso, usaremos la siguiente formula: 

**==> picture [164 x 29] intentionally omitted <==**

donde _m_ es el numero de posibles opiniones, _p_ es el vector con la distribucion de personas por opinion, _pi_ es el numero de personas con opinion _i_ , _v_ es el vector con los valores de todas las opiniones, es decir _vi_ es el valor de la opinion _i_ ; y mediana(p,v) corresponde al valor de la mediana de los valores de las opiniones de todas las personas que forman la poblacion de acuerdo a la distribucion _p_ . 

## **2.3. Formalizacion** 

Sea _n ∈_ N el numero total de personas. Sea _m ∈_ N el numero de opiniones posibles que pueden tener las personas. 

Sea _pi ∈_ 0 _..n_ el numero de personas que tienen como opinion inicial la opinion _i ∈_ 1 _..m_ 

Sea _vi ∈_ [0 _,_ 1] el valor real correspondiente a la opinion _i ∈_ 1 _..m_ 

Sea _ci,j ∈_ R[+] el costo del esfuerzo de mover una persona de opinion _i_ a la opinion _j_ , donde _i, j ∈_ 1 _..m_ . Obviamente _ci,i_ = 0 _, i ∈_ 1 _..m_ . 

Sea _cei ∈_ R[+] el costo extra de mover una persona a la posicion _i_ si dicha posicion estaba inicialmente sin personas _i ∈_ 1 _..m_ . 

Sea _ct ∈_ R[+] el costo total maximo permitido de todos los esfuerzos. 

Sea _maxM ∈_ N[+] el maximo numero de movimientos permitidos. 

El problema consiste en decidir que esfuerzos (donde cada esfuerzo consiste en mover un determinado numero de personas de una opinion _i_ a una opinion _j_ ) se haran tal que el costo total permitido para todos los esfuerzos no sea superado y que se minimice la polarizacion de la poblacion. 

Naturalmente, el numero de personas que se mueven de una opinion a otras, no puede ser mayor que el numero de personas que tenıan inicialmente esa opinion. 

Ademas, el numero de movimientos total va a estar limitado por un numero maximo de movimientos posibles. Mover una persona de la opinion _i_ a la opinion _j_ se contabilizara como _|j − i|_ movimientos. 

Y obviamente, cada persona tiene una y solo una opinion, tanto en la distribucion original, como en la resultante. 

Ahora, ¿cuanto cuesta una solucion? 

El costo de una solucion es la suma de los costos de cada movimiento. 

El costo de un movimiento de _x_ personas de la opinion _i_ a la opinion _j_ esta dado por _ci,j_ (1+ _pi/n_ ) _∗ x_ , si _pj >_ 0. En el caso en que _pj_ = 0, a ese costo se le suma _cej ∗ x_ . 

3 

**El Problema de Minimizar la Polarizacion presente en una Poblacion: MinPol** 

**Entrada:** _n ∈_ N _, m ∈_ N, _pi ∈_ 0 _..n, cei ∈_ R[+] , _ci,j ∈_ R[+] _, i, j ∈_ 1 _..m_ , _ct ∈_ R[+] _, maxM ∈_ N[+] 

**Salida:** _xi,j ∈_ N _, i ∈_ 1 _..m, j ∈_ 1 _..m_ son el numero de personas que pasaran de tener una opinion _i_ a una opinion _j_ . Tal que se minimice la polarizacion, respetando las restricciones propias del problema. 

## **2.4. ¿Entendimos el problema?** 

Una poblacion formada por 20 personas, considerando 5 posibles diferentes opiniones, se distribuyen como se muestra en el cuadro 1. 

|Num. personas por opinion|Opiniones|
|---|---|
|12<br>4<br>0<br>4<br>0|1<br>2<br>3<br>4<br>5|



Cuadro 1: Distribucion de poblacion por opinion. 

Los valores de las opiniones se aprecian en el cuadro 2. 

|Opiniones|Valor|
|---|---|
|1<br>2<br>3<br>4<br>5|0<br>0.25<br>0.5<br>0.75<br>1|



Cuadro 2: Valores de las opiniones posibles. 

El costo individual de ir de una opinion a otra se describe en el cuadro 3: 

|Costo|op. 1|op.2|op. 3|op. 4|op. 5|
|---|---|---|---|---|---|
|op. 1|0|2|4|5|7|
|op. 2|1|0|3|4|6|
|op. 3|3|2|0|2|4|
|op. 4|4|2|1|0|2|
|op. 5|8|5|3|2|0|



Cuadro 3: Costos individuales de los cambios de opinion. 

Adicionalmente en el cuadro 4 se muestra el costo extra del esfuerzo individual de pasar a una opinion de llegada cuando esta opinion inicialmente no era compartida por ninguna persona. Este costo extra solo se aplicara bajo el cumplimiento de la condicion anterior. 

El costo total maximo permitido es 20, y el numero maximo de movimientos es 18. En este caso la entrada se describirıa ası: 

4 

|Opiniones de llegada|Costo extra|
|---|---|
|1<br>2<br>3<br>4<br>5|1<br>2<br>1<br>1<br>3|



Cuadro 4: Costos extras de desplazamientos a opiniones inicialmente no compartidas por ninguno. 

**Entrada:** _n_ = 20 _, m_ = 5, _pi ∈_ N _, i ∈_ 1 _..m_ segun el cuadro 1, _ci,j ∈_ R[+] _, i, j ∈_ 1 _..m_ segun el cuadro 3, _cei ∈_ R[+] _, i ∈_ 1 _..m_ segun el cuadro 4, _ct_ = 20, _MaxMovs_ = 18. 

Describa al menos tres salidas diferentes para esta instancia, que cumpla todas las restricciones y calcule su respectiva polarizacion. 

¿Es alguna de ellas una solucion optima? Si no, describa una solucion optima. 

## **3. El proyecto: Modelamiento e Implementacion** 

Usted como ingeniero ha sido contratado para resolver el problema y debe: 

- Proponer un modelo generico para solucionar el problema. El modelo debe ser incluido en formato pdf y debe contener: parametros, variables, restricciones, funcion objetivo. El modelo debe utilizar notacion formal para que soporte cualquier instancia con la entrada definida en la Seccion 3.1. 

- Generar 5 instancias para retar a otros proyectos. Para cada instancia debe incluir la entrada y la salida esperada (el valor del optimo, o por lo menos el valor de la mejor solucion que su grupo haya encontrado) 

- Implementar el modelo generico en MiniZinc ( **Proyecto.mzn** ). 

- Incluir una tabla con pruebas realizadas sobre las instancias que se proveen con el proyecto y las 5 instancias creadas por su grupo de trabajo. Realice un analisis sobre los resultados obtenidos (incluya el analisis en el informe con el modelo). 

- Desarrollar una interfaz grafica con la tecnologıa de su predileccion que permita configurar o leer una entrada para el problema (la entrada debera convertirse a formato dzn para poder ser ejecutada por el modelo cumpliendo con las caracterısticas de la entrada definida en la Seccion 3.1) y visualizar la salida. Esta interfaz junto con el modelo serıa el entregable para el cliente y sera utilizada por algun operario. La interfaz debe incluir un boton que al presionarlo: 

   - Cree un archivo **DatosProyecto.dzn** con los datos proporcionados en la interfaz 

   - Ejecute el modelo generico **Proyecto.mzn** sobre los datos proporcionados 

   - Despliegue los resultados de la solucion 

- Incluya los archivos fuente de su implementacion grafica en un directorio llamado **ProyectoGUIFuentes** 

Para mayor informacion sobre la forma de ejecutar un modelo MiniZinc a traves de lınea de comandos visite: 

- Modelamiento basico en MiniZinc: `https://www.minizinc.org/doc-2.2.3/en/modelling. html` 

5 

   - Modelos mas complejos: `https://www.minizinc.org/doc-2.2.3/en/modelling2.html` 

- Hacer un vídeo de hasta 15 minutos que muestre su aplicación en funcionamiento. Cada integrante necesita participar en el video. Se de-be explicar el modelo con cada uno de sus componentes, asÍ como las decisiones de im-plementación más destacadas, y realizar al menos dos pruebas con distintas configuraciones en las que se muestren las soluciones en la interfaz gráfica. Se debe incluir un enlace al video en el archivo pdf del informe. 

## **3.1. Entrada** 

La entrada se leera de un archivo de texto *.mpl con la siguiente informacion: 

1. La primera lınea contiene un entero indicando el numero de personas(es decir, conteniendo _n_ ). 

2. La segunda lınea contiene un entero indicando el numero de posibles opiniones (es decir, conteniendo _m_ ). 

3. La siguiente lınea contiene, una lista de _m_ valores enteros correspondientes a la distribucion de las personas segun su opinion inicial, separados por comas, _pi, i ∈_ 1 _..m_ . La suma de esos valores es _n_ . 

4. La siguiente lınea contiene, una lista de _m_ valores reales correspondientes a los valores de las opiniones posibles separados por comas, correspondientes, en su orden, a _vi, i ∈_ 1 _..m_ . 

5. La siguiente lınea contiene, una lista de _m_ valores reales separados por comas, correspondientes, en su orden, a los valores de los costos extras de las opiniones posibles, es decir a _cei, i ∈_ 1 _..m_ . 

6. Las siguientes _m_ lıneas, contienen, cada una, una lista de _m_ valores separados por comas, correspondientes, en su orden, a los costos del desplazamiento de cada opinion a las _m_ opiniones posibles; es decir, cada lınea contiene _ci,j, i, j ∈_ 1 _..m_ . 

7. La siguiente lınea contiene, un valor real correspondiente al costo total maximo permitido (es decir, conteniendo _ct_ ). 

8. La siguiente lınea contiene, un valor correspondiente al costo total maximo permitido (es decir, conteniendo _MaxMovs_ ). 

El archivo correspondiente a la entrada del ejemplo de la seccion 2.4 serıa: 

```
20
5
12,4,0,4,0
0,0.25,0.5,0.75,1
1,2,1,1,3
0,2,4,5,7
1,0,3,4,6
3,2,0,2,4
4,2,1,0,2
8,5,3,2,0
20
18
```

En el campus se compartiran ejemplos de entradas con sus respectivas salidas (Nota: es posible que en algunos casos haya varias soluciones que tengan el mismo valor para la funcion objetivo) 

6 

**3.2. Sobre el Informe** 

El grupo debera entregar un informe del proyecto, en formato pdf, que contenga, al menos, los siguientes aspectos: 

- El modelo: una descripcion del modelo y una justificacion de su adecuacion al problema planteado. 

- Detalles importantes de implementacion: lo mas relevante de la implementacion, sin incluir codigo. 

- El analisis de los arboles generados por su modelo para el ejemplo, y explicar sobre el como funciono el mecanismo de _Branch and Bound_ . 

Pruebas: descripcion de las pruebas realizadas a su implementacion. 

Analisis: de los resultados de las pruebas realizadas, buscando responder a los diferentes criterios de evaluacion definidos en la rubrica. Desarrolle y soporte su analisis utilizando los metodos apropiados (tablas, graficos, indicadores estadısticos), donde puedan apreciarse las variaciones de acuerdo al tama˜no y naturaleza de los datos de entrada. Explique claramente el significado de sus datos y como se analizaron. 

Un enlace al video explicatorio de la interfaz grafica 

- Conclusiones: Esta es una de las partes mas interesantes del trabajo (pero no por ello la que mas vale). En ella se espera que usted analice los resultados obtenidos y **justifique** claramente sus 

## **3.3. Grupos de trabajo** 

El proyecto puede ser desarrollado por grupos de maximo 4 personas. 

## **4. Entrega, sustentacion y evaluacion** 

## **4.1. Entrega** 

La entrega se debe realizar vıa el campus virtual en las fechas previstas para ello, por uno solo de los integrantes del grupo. **La fecha de entrega lımite es el** 22 **de** julio **de 202** 6 **a las 23:59.** Se debe subir al campus virtual en el enlace correspondiente a este proyecto un archivo comprimido **.zip** que siga la convencion _CodigodeEstudiante1-CodigodeEstudiante2-CodigodeEstudiante3-CodigodeEstudiante4Proyecto2-AdaII.zip_ . El comprimido debera contener: 

1. Archivo **Readme.txt** que describa todos los archivos entregados y las instrucciones para ejecutar la aplicacion. 

2. Archivo **Informe.pdf** acorde a la Seccion 3.2. Recuerde incluir el link al video explicatorio. 

3. Archivo **Proyecto.mzn** con la implementacion del modelo 

4. Directorio **DatosProyecto** con los datos con que fue probado su modelo. 

5. Directorio **ProyectoGUIFuentes** con los archivos fuente de la implementacion de la interfaz grafica 

6. Directorio **MisInstancias** con las 5 instancias generadas por su equipo de trabajo para retar a otros proyectos que resuelvan el mismo problema. 

7 

## **4.2. Evaluacion** 

La evaluacion de cada proyecto se hara de acuerdo a la rubrica publicada en el campus virtual, dise˜nada para observar los indicadores de logro asociados a este proyecto. 

8 

