from xml.etree.cElementTree import Element, ElementTree, SubElement
from datetime import datetime
from plantilla_pdf import xml_to_pdf


def info_element(elemento_padre: Element, compañia: str, logo: str):

    info = SubElement(elemento_padre, 'info', company=compañia, logo = logo)


def titulo_element(elemento_padre: Element, titulo: str, fecha: str, autores: str):

    title = SubElement(elemento_padre, 'title', title=titulo, date=fecha, people=autores)


def imagen_element(elemento_padre: Element, nombre: str, imagen: str):

    image = SubElement(elemento_padre, 'imageslide', title=nombre, image=imagen)


def seccion_element(elemento_padre: Element, nombre_seccion: str):

    seccion = SubElement(elemento_padre, 'section', name=nombre_seccion)


def pagina_element(elemento_padre: Element, titulo: str, parrafo: str):

    pagina_normal = SubElement(elemento_padre, 'slide', title=titulo)

    for linea in parrafo.split('\n'):

        entrada = SubElement(pagina_normal, 'p')
        entrada.text = linea


def create_xml_presentation(equipo: str, season: int, ganador: str):

    elem = Element('presentation')
    usuario = 'Alvaro Pereira, 202114948@alu.comillas.edu'
    info_element(elem, f'{equipo}', 'logo.png')

    titulo = f'Estadísticas de {equipo} para la temporada {season - 1}-{season}'
    titulo_element(elem, titulo, str(datetime.now().date()), usuario)

    seccion_element(elem, 'Estadísticas generales del equipo')
    imagen_element(elem, f'{equipo}, {season - 1}-{season}', 'df0.png')
    imagen_element(elem, f'Leyenda', 'leyenda0.png')

    seccion_element(elem, 'Estadísticas por partido del equipo')
    imagen_element(elem, f'{equipo}, {season - 1}-{season}', 'df1.png')
    imagen_element(elem, f'Leyenda', 'leyenda1.png')

    pagina_element(elem, 'Nuestra predicción', ganador)

    return elem


def crear_xml(nombre: str, season: int, ganador: str):

    archivo = create_xml_presentation(nombre, season, ganador)

    return archivo


def crear_presentacion(equipo: str, season: int, ganador: str):

    archivo = crear_xml(equipo, season, ganador)

    xml_to_pdf(archivo, equipo)
