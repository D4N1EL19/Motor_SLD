
# Motor de Resolución SLD 

1. **Unificación (`unificar`, `unificar_variable`)**
2. **Aplicación de sustituciones (`aplicar_sustitucion`)**
3. **Resolución SLD (`resolver_sld`)**
4. **Consultas múltiples (`buscar_recetas_por_condicion`)**
5. **Guardado de resultados (`guardar_resultados`)**

##  1. Unificación

La unificación es el proceso de encontrar una sustitución de variables que haga que dos expresiones sean iguales.

### Función principal: `unificar(x, y, sustitucion=None)`

Compara dos términos `x` y `y` y devuelve un diccionario con las sustituciones que los hacen coincidir.

Casos manejados:

- Si `x == y` → ya son iguales.
- Si uno de los términos es una variable lógica (cadena en mayúsculas) → se unifican asignando un valor.
- Si ambos son tuplas (predicados) → se unifican recursivamente, comparando nombre y argumentos.
- Si no hay coincidencia posible → retorna `None`.

### Función auxiliar: `unificar_variable(var, valor, sustitucion)`

Gestiona el caso en que uno de los términos es una variable lógica:

1. Si ya existe una sustitución previa, se aplica recursivamente.
2. Si el valor también está sustituido, se resuelve de forma recursiva.
3. Si no hay conflicto, se crea una nueva copia del diccionario con la sustitución añadida.

Ejemplo:

```python
unificar(("es_picante", "X"), ("es_picante", "chile_guajillo"))
# → {"X": "chile_guajillo"}
```

## 2. Aplicar sustituciones

La función `aplicar_sustitucion(meta, sustitucion)` reemplaza las variables en una meta con los valores ya unificados.

```python
def aplicar_sustitucion(meta, sustitucion):
    predicado, *args = meta
    nuevos_args = []
    for a in args:
        if isinstance(a, str) and a in sustitucion:
            nuevos_args.append(sustitucion[a])
        else:
            nuevos_args.append(a)
    return (predicado, *nuevos_args)
```

## 3. Resolución SLD `resolver_sld`

Esta es la función central del motor lógico.  
Simula el proceso de razonamiento de Prolog: selecciona una meta, la intenta resolver con los hechos y reglas, y continúa recursivamente hasta que no queden metas pendientes.

```python
def resolver_sld(metas, hechos, reglas, sustitucion=None, profundidad=0):
```

### Flujo del algoritmo:

1. **Caso base:** si ya no quedan metas, se ha encontrado una solución → imprime la sustitución
2. **Toma la primera meta** (`meta_actual`) y conserva el resto (`resto`)
3. **Intenta unificar con los hechos:**  
   Si hay coincidencia, aplica la sustitución y continúa resolviendo las metas restantes
4. **Intenta unificar con reglas:**  
   Si la cabeza de una regla coincide, sustituye la meta actual por el cuerpo de la regla y continúa resolviendo
5. Cada paso recursivo aumenta la profundidad 

## 4. Consultas múltiples

La función `buscar_recetas_por_condicion(condicion, hechos, reglas)` automatiza consultas sobre varias recetas, ejecutando el motor SLD para cada una.

- Extrae todas las recetas de los hechos.
- Llama a `resolver_sld([(condicion, receta)], ...)` para probar si cumple la condición.
- Muestra resultados

```python
recetas_poco = buscar_recetas_por_condicion("poco_picante", HECHOS, REGLAS)
recetas_picante = buscar_recetas_por_condicion("picante", HECHOS, REGLAS)
```



## 4. Versiones Iterativas de las Funciones `unificar` y `resolver_sld`
Nos pidio en clase que tengamos ambos metodos recursivo e iterativo de las funciones
###  `unificar` — versión iterativa

```python
def unificar_iterativo(x, y, sustitucion=None):
    if sustitucion is None:
        sustitucion = {}

    # pila de pares a unificar
    pila = [(x, y)]

    while pila:
        a, b = pila.pop()

        # caso idéntico
        if a == b:
            continue

        # si a es variable
        if isinstance(a, str) and a.isupper():
            if a in sustitucion:
                pila.append((sustitucion[a], b))
            elif isinstance(b, str) and b in sustitucion:
                pila.append((a, sustitucion[b]))
            else:
                sustitucion = sustitucion.copy()
                sustitucion[a] = b
            continue

        # si b es variable
        if isinstance(b, str) and b.isupper():
            pila.append((b, a))
            continue

        # si ambos son tuplas (predicados)
        if isinstance(a, tuple) and isinstance(b, tuple):
            if a[0] != b[0] or len(a) != len(b):
                return None
            # añadir todos los argumentos a la pila
            for sub_a, sub_b in zip(a[1:], b[1:]):
                pila.append((sub_a, sub_b))
            continue

        # si no coinciden y no son estructuras comparables
        return None

    return sustitucion
```

### Cómo funciona

1. Se inicializa una pila con el par de términos inicial `(x, y)`.
2. Mientras haya elementos en la pila:
   - Se extrae un par `(a, b)`.
   - Se comparan y se manejan los casos:
     - Si son iguales → se ignoran.
     - Si uno es variable → se agrega una sustitución.
     - Si ambos son tuplas → se añaden sus subcomponentes a la pila.
3. Si en algún momento no se pueden igualar → devuelve `None`.
4. Si la pila se vacía sin fallos → se devuelve la sustitución final.

### Ejemplo
``` python
x1 = ("padre", "juan", "X")
x2 = ("padre", "juan", "maria")

print(unificar(x1, x2))               # {'X': 'maria'}
print(unificar_iterativo(x1, x2))     # {'X': 'maria'}
```


### `resolver_sld` — versión iterativa

```python
def resolver_sld_iterativo(metas_iniciales, hechos, reglas):
    pila = [(metas_iniciales, {}, 0)]
    resultados = []

    while pila:
        metas, sustitucion, profundidad = pila.pop()

        # Caso base: sin metas → éxito
        if not metas:
            print("Éxito con sustitución:", sustitucion)
            resultados.append(sustitucion)
            continue

        meta_actual, *resto = metas
        print("  " * profundidad + f"Meta actual: {meta_actual}")

        # 1. Intentar unificar con hechos
        for hecho in hechos:
            sigma = unificar(meta_actual, hecho, sustitucion)
            if sigma is not None:
                print("  " * profundidad + f"Unifica con hecho {hecho} -> {sigma}")
                nuevas_metas = [aplicar_sustitucion(m, sigma) for m in resto]
                pila.append((nuevas_metas, sigma, profundidad + 1))

        # 2. Intentar unificar con reglas
        for cabeza, cuerpo in reglas:
            sigma = unificar(meta_actual, cabeza, sustitucion)
            if sigma is not None:
                print("  " * profundidad + f"Usa regla {cabeza} :- {cuerpo} -> {sigma}")
                nuevas_metas = [aplicar_sustitucion(m, sigma) for m in list(cuerpo) + resto]
                pila.append((nuevas_metas, sigma, profundidad + 1))

    return resultados
```


### Cómo funciona

1. Cada elemento de la pila representa un estado de razonamiento:
   - `metas`: lista de objetivos pendientes.
   - `sustitucion`: asignaciones actuales.
2. En cada iteración del `while`:
   - Si no quedan metas, se encontró una solución → se guarda.
   - Si hay metas pendientes:
     - Se selecciona la primera meta.
     - Se intenta unificar con hechos y reglas.
     - Cada unificación válida genera un nuevo estado que se apila.
3. El algoritmo continúa hasta agotar todos los caminos posibles.

