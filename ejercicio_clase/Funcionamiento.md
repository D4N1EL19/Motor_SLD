# **Ejercicio de clase con el metodo SLD**
El objetivo del metodo SLD es obtener una sustitucion que conduzca a la meta vacía. La meta vacia significa que la consulta es verdadera. Para eso seguimos lo siguientes pasos en python
## **Base de conocimiento**
La base de conocimiento nos la dio en clase. Son diccionarios separados por echos
```python
firmas = {
    "luis": ["contrato456"],
    "ana": ["contrato789"]
}

contratos_validos = ["contrato456", "contrato789"]

clausulas = {
    "contrato456": ["confidencialidad", "no_competencia"],
    "contrato789": ["uso_datos"]
}
```
## **1. Hacer la funcion de unificacion**
Matimaticamente lo que queremos hacer es encontrar θ (theta) que son las sustituciones
para eso tenemos que poner ciertas reglas de nomenclatura. Si es variable empieza por MAYUSCULAS, si es un valor esta en minusculas 
1. Inicialización de la sustitución
    Si `sustitucion` es `None`, se crea un nuevo diccionario vacío:
     ```python
     if sustitucion is None:
         sustitucion = {}
     ```

2. Comprobación de igualdad directa
   - Si `x` y `y` son iguales, no hay necesidad de sustituciones.
     ```python
     if x == y:
         return sustitucion
     ```

3. Caso 1: `x` es una variable
   - Si `x` es una cadena y comienza con mayúscula (por ejemplo, `"Contrato"`), se considera una variable.
   - Se llama a `unificar_var(x, y, sustitucion)`.

     ```python
     if isinstance(x, str) and x[0].isupper():
         return unificar_var(x, y, sustitucion)
     ```

4. Caso 2: `y` es una variable
   - Si `y` cumple las mismas condiciones, se intercambian los argumentos:
     ```python
     if isinstance(y, str) and y[0].isupper():
         return unificar_var(y, x, sustitucion)
     ```

5. Caso sin coincidencia posible
   - Si ninguna condición se cumple, la unificación falla:
     ```python
     return None
     ```

Para definir una sustitución entre una variable y un valor, o resolverla si ya existe una relación previa creamos la funcion `unificar_var()`.

1. Verificar si la variable ya tiene una sustitución
   - Si la variable `var` ya está en el diccionario, se vuelve a intentar unificar su valor asignado con el nuevo `valor`:
     ```python
     if var in sustitucion:
         return unificar(sustitucion[var], valor, sustitucion)
     ```

2. **Verificar si el valor también es una variable ya sustituida**
   - Si `valor` es una variable y también está en las sustituciones, se unifica con su valor asignado:
     ```python
     if isinstance(valor, str) and valor[0].isupper() and valor in sustitucion:
         return unificar(var, sustitucion[valor], sustitucion)
     ```

3. **Crear o extender la sustitución**
   - Se copia el diccionario para no modificar el original directamente
   - Se añade la nueva relación `var = valor`:
     ```python
     sustitucion = sustitucion.copy()
     sustitucion[var] = valor
     return sustitucion
     ```



Lo que logramos con esto es: 

```python
unificar("X", "juan")
{'X': 'juan'}

unificar("X", "Y")
{'X': 'Y'}

unificar("juan", "juan")
{}
```
## **2. Por cada regla hacer una funcion SLD**
Lo que queremos hacer es representar las sub reglas de la clausula de Horn
`tiene_obligacion(Persona, Obligacion) :- firma(Persona, Contrato), contrato_valido(Contrato), clausula(Contrato, Obligacion).`

```python
def resolver_firma(persona, contrato):
    sustituciones = []
    for p, contratos in firmas.items():
        for c in contratos:
            subs = unificar(persona, p)
            if subs is not None:
                subs = unificar(contrato, c, subs)
                if subs is not None:
                    sustituciones.append(subs)
    return sustituciones
```
### **Pasos de las funcion**
1. Inicializar la lista de resultados
    * `sustituciones = []` para recoger todas las sustituciones válidas encontradas
2. Recorrer cada entrada de firmas  
    * Por cada par `(p, contratos) en firmas.items()` donde `p` representa la persona registrada y `contratos` es la lista de contratos asociados a `p`
3. Recorrer cada contrato `c` de la lista `contratos`
    * Iterar `for c in contratos:` para probar cada pareja `(p, c)`
4. Unificar la persona de la consulta con `p`
    * `subs = unificar(persona, p)`
    * Si la unificación falla `subs is None` → seguir con el siguiente  `c` 
    * Si tiene éxito → `subs` contiene una posible sustitucion que hace coincidir `persona` con `p`.
5. Conservar el contexto y unificar el `contrato`
    * `subs = unificar(contrato, c, subs)`
    * Ejecuta la segunda unificación usando las posibles sustituciones previas.
    * Si falla → descarta esta pareja `(p, c)` y continua.
    * Si tiene éxito → subs ahora es la sustitución completa para ambos.
6. Devolver resultados
    Al terminar las iteraciones, `return sustituciones` devuelve la lista de todas las sustituciones encontradas.

### **Resto de las sub reglas**
``` python
def resolver_contrato_valido(contrato):
    sustituciones = []
    for c in contratos_validos:
        subs = unificar(contrato, c)
        if subs is not None:
            sustituciones.append(subs)
    return sustituciones

def resolver_clausula(contrato, obligacion):
    sustituciones = []
    for c, obligaciones in clausulas.items():
        for o in obligaciones:
            subs = unificar(contrato, c)
            if subs is not None:
                subs = unificar(obligacion, o, subs)
                if subs is not None:
                    sustituciones.append(subs)
    return sustituciones
```

## **3. Función principal `tiene_obligacion()`**

Esta función representa la cláusula de Horn completa donde una persona tiene una obligacion si:
1. Firmó un contrato `firma(Persona, Contrato)`,
2. El contrato es válido `contrato_valido(Contrato)`
3. La cláusula correspondiente existe en el contrato `clausula(Contrato, Obligacion)`.

La implementación en Python utiliza las tres funciones de resolución anteriores para simular el método SLD encadenando las sustituciones.

```python
def tiene_obligacion(persona, obligacion):
    resultados = []
    # Paso 1: resolver firma(Persona, Contrato)
    for s1 in resolver_firma(persona, "Contrato"):
        contrato = s1["Contrato"]

        # Paso 2: contrato_valido(Contrato)
        for s2 in resolver_contrato_valido(contrato):
            s3 = s1.copy()
            s3.update(s2)

            # Paso 3: clausula(Contrato, Obligacion)
            for s4 in resolver_clausula(contrato, obligacion):
                s5 = s3.copy()
                s5.update(s4)
                resultados.append(s5)
    return resultados
```

### **Pasos de la función**

1. **Inicializar resultados**  
   Se crea una lista vacía `resultados = []` que almacenará todas las sustituciones completas que satisfacen la regla.

2. **Primera meta: `firma(Persona, Contrato)`**  
   Se llama a `resolver_firma()` con los argumentos de la consulta:
   ```python
   for s1 in resolver_firma(persona, "Contrato"):
   ```
   Cada `s1` representa una posible sustitución (por ejemplo, `{"Contrato": "contrato456"}`).

3. **Segunda meta: `contrato_valido(Contrato)`**  
   Con el contrato encontrado en la primera etapa, se verifica si ese contrato es válido:
   ```python
   for s2 in resolver_contrato_valido(contrato):
   ```
   Si el contrato no está en la lista de válidos, no se continúa con esa rama.

4. **Combinar sustituciones**  
   Se fusionan las sustituciones obtenidas de los dos primeros pasos:
   ```python
   s3 = s1.copy()
   s3.update(s2)
   ```
    Se hace de esta manera para evitar perder el contexto anterior en `s1` o `s2`
5. **Tercera meta: `clausula(Contrato, Obligacion)`**  
   Se busca si el contrato contiene la obligación indicada:
   ```python
   for s4 in resolver_clausula(contrato, obligacion):
   ```
   Si la unificación es exitosa, se obtiene una nueva sustitución `s5`.

6. **Guardar resultados finales**  
   Si todas las metas se cumplen secuencialmente, se guarda la sustitución resultante:
   ```python
   resultados.append(s5)
   ```

7. **Devolver las soluciones**  
   Al finalizar, `tiene_obligacion` devuelve una lista con todas las sustituciones que hacen verdadera la consulta:
   ```python
   return resultados
   ```

### **Ejemplo de ejecución**
consulta: 
```python
tiene_obligacion("luis", "confidencialidad")
```

Proceso interno:
1. `resolver_firma("luis", "Contrato")` → `{"Contrato": "contrato456"}`
2. `resolver_contrato_valido("contrato456")` → éxito
3. `resolver_clausula("contrato456", "confidencialidad")` → éxito

Resultado final:
```python
[{"Contrato": "contrato456"}]
```
consulta:
```python
tiene_obligacion("ana", "confidencialidad")
```

Proceso interno:
1. `resolver_firma("ana", "Contrato")` → `{"Contrato": "contrato789"}`
2. `resolver_contrato_valido("contrato789")` → éxito
3. `resolver_clausula("contrato789", "confidencialidad")` → falla

resultado final:
```python
[]
```