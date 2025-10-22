# ----------------------------------
#       BASE DE CONOCIMIENTO
# ----------------------------------

firmas = {
    "luis": ["contrato456"],
    "ana": ["contrato789"]
}

contratos_validos = ["contrato456", "contrato789"]

clausulas = {
    "contrato456": ["confidencialidad", "no_competencia"],
    "contrato789": ["uso_datos"]
}


# ---------------------------------------
#       PASO 1. HACER LA UNIFICACIÓN
# ---------------------------------------

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

def es_variable(x):
    return isinstance(x, str) and x[0].isupper()

def unificar_var(var, valor, sustitucion):
    if var in sustitucion:
        return unificar(sustitucion[var], valor, sustitucion)
    if es_variable(valor) and valor in sustitucion:
        return unificar(var, sustitucion[valor], sustitucion)
    sustitucion = sustitucion.copy()
    sustitucion[var] = valor
    return sustitucion

# --------------------------------------------------
#                     PASO 2
#     Por cada regla hacer una función que use 
#     la implementación de unificación como motor SLD
#
# --------------------------------------------------

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

# --------------------------------------------------
#         PASO 3. resolver la regla general
# --------------------------------------------------

def tiene_obligacion(persona, obligacion):
    resultados = []
    for s1 in resolver_firma(persona, "Contrato"):
        contrato = s1["Contrato"]
        for s2 in resolver_contrato_valido(contrato):
            s3 = s1.copy()
            s3.update(s2)
            for s4 in resolver_clausula(contrato, obligacion):
                s5 = s3.copy()
                s5.update(s4)
                resultados.append(s5)
    return resultados


# --------------------------------------------------
#                 EJEMPLO DE USO
# --------------------------------------------------

if __name__ == "__main__":
    consultas = [("luis", "confidencialidad"), ("ana", "confidencialidad")]
    for persona, obligacion in consultas:
        resultado = tiene_obligacion(persona, obligacion)
        print(f"{persona} tiene obligación de {obligacion}: {bool(resultado)}")
