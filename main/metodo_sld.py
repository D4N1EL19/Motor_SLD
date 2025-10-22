from base_conocimiento import ingredientes_receta, ingredientes_picantes

# --- unificacion ---
def es_variable(x):
    return isinstance(x, str) and x[0].isupper()

def unificar(x, y, sustitucion=None):
    if sustitucion is None:
        sustitucion = {}
    if x == y:
        return sustitucion
    if es_variable(x):
        return unificar_var(x, y, sustitucion)
    if es_variable(y):
        return unificar_var(y, x, sustitucion)
    return None

def unificar_var(var, valor, sustitucion):
    if var in sustitucion:
        return unificar(sustitucion[var], valor, sustitucion)
    if es_variable(valor) and valor in sustitucion:
        return unificar(var, sustitucion[valor], sustitucion)
    sustitucion = sustitucion.copy()
    sustitucion[var] = valor
    return sustitucion

# --- subreglas ---
def resolver_ingrediente_en_receta(receta, ingrediente):
    sustituciones = []
    for r, ingredientes in ingredientes_receta.items():
        for ing in ingredientes:
            subs = unificar(receta, r)
            if subs is not None:
                subs = unificar(ingrediente, ing, subs)
                if subs is not None:
                    sustituciones.append(subs)
    return sustituciones

def resolver_miembro(ingrediente, lista_picante):
    sustituciones = []
    for ing in lista_picante:
        subs = unificar(ingrediente, ing)
        if subs is not None:
            sustituciones.append(subs)
    return sustituciones

# --- reglas principales ---
def es_poco_picante(receta):
    resultados = []
    ingredientes_poco_picantes = ingredientes_picantes["poco_picante"]
    for s1 in resolver_ingrediente_en_receta(receta, "Ingrediente"):
        ingrediente = s1["Ingrediente"]
        for s2 in resolver_miembro(ingrediente, ingredientes_poco_picantes):
            s3 = s1.copy()
            s3.update(s2)
            resultados.append(s3)
    return resultados

def es_picante(receta):
    resultados = []
    ingredientes_fuertes = ingredientes_picantes["picante"]
    for s1 in resolver_ingrediente_en_receta(receta, "Ingrediente"):
        ingrediente = s1["Ingrediente"]
        for s2 in resolver_miembro(ingrediente, ingredientes_fuertes):
            s3 = s1.copy()
            s3.update(s2)
            resultados.append(s3)
    return resultados


if __name__ == "__main__":
    recetas = list(ingredientes_receta.keys())
    recetas_picantes = [r for r in recetas if es_picante(r)]
    print("Recetas picantes:", recetas_picantes)

    # Todas las recetas poco picantes
    recetas_poco_picantes = [r for r in recetas if es_poco_picante(r)]
    print("Recetas poco picantes:", recetas_poco_picantes)

