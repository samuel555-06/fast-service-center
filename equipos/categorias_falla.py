# Categorías de falla según el tipo de equipo (línea blanca o teléfonos)

CATEGORIAS_LINEA_BLANCA = {
    'Compresor / motor': ['compresor', 'motor', 'no enfria', 'no enfría'],
    'Control electrónico / placa': ['placa', 'control electronico', 'control electrónico', 'tarjeta', 'panel de control'],
    'Fugas de agua / gas': ['fuga', 'gotea', 'gas', 'liquido', 'líquido'],
    'No enciende': ['no enciende', 'no prende', 'no arranca'],
    'Ruido / vibración excesiva': ['ruido', 'vibra', 'vibración', 'vibracion'],
    'Puerta / bisagra': ['puerta', 'bisagra', 'sello', 'empaque'],
    'Otro': [],
}

CATEGORIAS_TELEFONO = {
    'Pantalla / táctil': ['pantalla', 'tactil', 'táctil', 'display', 'rota', 'quebrada'],
    'Batería / carga': ['bateria', 'batería', 'carga', 'cargador', 'no carga'],
    'No enciende': ['no enciende', 'no prende', 'no arranca'],
    'Cámara': ['camara', 'cámara', 'foto'],
    'Bocina / micrófono': ['bocina', 'microfono', 'micrófono', 'audio', 'sonido'],
    'Daño por agua': ['agua', 'mojado', 'humedad', 'liquido', 'líquido'],
    'Software': ['software', 'sistema', 'lento', 'virus', 'actualizacion', 'actualización'],
    'Otro': [],
}

# Palabras clave para reconocer si el tipo de equipo es línea blanca o teléfono
PALABRAS_LINEA_BLANCA = [
    'lavadora', 'nevera', 'refrigerador', 'refrigeradora', 'estufa',
    'microondas', 'secadora', 'congelador', 'lavaplatos',
]
PALABRAS_TELEFONO = ['telefono', 'teléfono', 'celular', 'smartphone', 'movil', 'móvil']


def _grupo_categorias(tipo_equipo: str) -> dict:
    tipo = tipo_equipo.lower()
    if any(palabra in tipo for palabra in PALABRAS_TELEFONO):
        return CATEGORIAS_TELEFONO
    if any(palabra in tipo for palabra in PALABRAS_LINEA_BLANCA):
        return CATEGORIAS_LINEA_BLANCA
    # Si no reconocemos el tipo, usamos línea blanca como default
    # (ajustable después si el taller diversifica más tipos de equipo)
    return CATEGORIAS_LINEA_BLANCA


def clasificar_falla(tipo_equipo: str, texto_falla: str) -> str:
    categorias = _grupo_categorias(tipo_equipo)
    texto = texto_falla.lower()
    for categoria, palabras_clave in categorias.items():
        if categoria == 'Otro':
            continue
        if any(palabra in texto for palabra in palabras_clave):
            return categoria
    return 'Otro'