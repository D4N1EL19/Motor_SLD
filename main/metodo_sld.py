from base_conocimiento import HECHOS, REGLAS

# -----------------------------------
#           UNIFICACIÓN
# -----------------------------------
def unificar(x, y, sustitucion=None):
    if sustitucion is None:
        sustitucion = {}

    if x == y:
        return sustitucion

    if isinstance(x, str) and x.isupper():
        return unificar_variable(x, y, sustitucion)

    if isinstance(y, str) and y.isupper():
        return unificar_variable(y, x, sustitucion)

    if isinstance(x, tuple) and isinstance(y, tuple):
        if x[0] != y[0] or len(x) != len(y):
            return None
        for a, b in zip(x[1:], y[1:]):
            sustitucion = unificar(a, b, sustitucion)
            if sustitucion is None:
                return None
        return sustitucion

    return None


def unificar_variable(var, valor, sustitucion):
    if var in sustitucion:
        return unificar(sustitucion[var], valor, sustitucion)
    if valor in sustitucion:
        return unificar(var, sustitucion[valor], sustitucion)
    if var == valor:
        return sustitucion
    nueva = sustitucion.copy()
    nueva[var] = valor
    return nueva


# -----------------------------------
#       APLICAR SUSTITUCIÓN
# -----------------------------------
def aplicar_sustitucion(meta, sustitucion):
    predicado, *args = meta
    nuevos_args = []
    for a in args:
        if isinstance(a, str) and a in sustitucion:
            nuevos_args.append(sustitucion[a])
        else:
            nuevos_args.append(a)
    return (predicado, *nuevos_args)


# -----------------------------------
#          RESOLUCIÓN SLD
# -----------------------------------
def resolver_sld(metas, hechos, reglas, sustitucion=None, profundidad=0):
    if sustitucion is None:
        sustitucion = {}

    if not metas:
        print("Éxito con sustitución:", sustitucion)
        return [sustitucion]

    meta_actual, *resto = metas
    resultados = []

    print("  " * profundidad + f"Meta actual: {meta_actual}")

    # 1. Intentar unificar con hechos
    for hecho in hechos:
        sigma = unificar(meta_actual, hecho, sustitucion)
        if sigma is not None:
            print("  " * profundidad + f"Unifica con hecho {hecho} -> {sigma}")
            nuevas_metas = [aplicar_sustitucion(m, sigma) for m in resto]
            resultados += resolver_sld(nuevas_metas, hechos, reglas, sigma, profundidad + 1)

    # 2. Intentar unificar con reglas
    for cabeza, cuerpo in reglas:
        sigma = unificar(meta_actual, cabeza, sustitucion)
        if sigma is not None:
            print("  " * profundidad + f"Usa regla {cabeza} :- {cuerpo} -> {sigma}")
            nuevas_metas = [aplicar_sustitucion(m, sigma) for m in list(cuerpo) + resto]
            resultados += resolver_sld(nuevas_metas, hechos, reglas, sigma, profundidad + 1)

    return resultados


# -----------------------------------
#             CONSULTA
# -----------------------------------
def buscar_recetas_por_condicion(condicion, hechos, reglas):
    print(f"\n=== Buscando recetas {condicion} ===\n")
    recetas_encontradas = set()

    # extrae todas las recetas que aparecen en los hechos
    recetas = {h[1] for h in hechos if len(h) >= 3 and isinstance(h[1], str)}

    for receta in recetas:
        print(f"\nProbando receta: {receta}")
        resultados = resolver_sld([(condicion, receta)], hechos, reglas)
        if resultados:
            recetas_encontradas.add(receta)

    print(f"\n Recetas {condicion.replace('_', ' ')}:")
    for r in recetas_encontradas:
        print("  -", r)
    print(f"Total: {len(recetas_encontradas)}")

    return recetas_encontradas


# -----------------------------------
#       PROGRAMA PRINCIPAL
# -----------------------------------
if __name__ == "__main__":
    recetas_poco = buscar_recetas_por_condicion("poco_picante", HECHOS, REGLAS)
    recetas_picante = buscar_recetas_por_condicion("picante", HECHOS, REGLAS)
