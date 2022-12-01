import requests
import re
import os
import pandas as pd
import dataframe_image as dfi

from selenium import webdriver
from reporte import crear_presentacion
from datetime import datetime

# La temporada en la que nos encontramos
SEASON = 2023
URL = 'https://www.sportytrader.es/pronosticos/baloncesto/usa/nba-306/'
headers = None
team_actual = None
partidos = 0
team_code = None


def extract(configuracion: str = 'config.txt', team: str = 'Celtics') -> dict or False:
    '''
    Extrae las estadísticas de los jugadores de un equipo esta útlima temporada
    '''
    global headers, team_actual, partidos, team_code

    team_actual = team

    with open(configuracion, 'r') as archivo:
        clave = archivo.readline()
    key = re.search('\w+$', clave).group()

    url_teams = f'https://api.sportsdata.io/v3/nba/scores/json/TeamSeasonStats/{SEASON}'

    headers = {
    'Ocp-Apim-Subscription-Key': key
    }

    dicc = requests.get(url=url_teams, headers=headers)
    if dicc.status_code >= 300:
        return False

    equipo = None
    for equipos in dicc.json():
        if team in equipos['Name']:
            equipo = equipos
    
    if equipo is None:
        return False
    
    team_code = equipo['Team']
    partidos = equipo['Games']

    url_jugadores = f'https://api.sportsdata.io/v3/nba/stats/json/PlayerSeasonStatsByTeam/{SEASON}/{team_code}'

    team_stats = requests.get(url=url_jugadores, headers=headers)

    if team_stats.status_code >= 300 or not team_stats.json():
        return False

    return team_stats.json()


def transform(team_stats: list or False) -> list or None:

    if not team_stats:
        return [None, None]

    claves_1 = {
            'Name': 'Player', 'Position': 'P', 'Games': 'G', 'Minutes': 'Min',
            'FieldGoalsMade': 'FGM', 'FieldGoalsAttempted': 'FGA',
            'FreeThrowsMade': 'FTM', 'FreeThrowsAttempted': 'FTA',
            'ThreePointersMade': 'TPM', 'ThreePointersAttempted': 'TPA',
            'Rebounds': 'Reb', 'Assists': 'A', 'Steals': 'Stl',
            'BlockedShots': 'BkS', 'Turnovers': 'To', 'PlusMinus': '+/-',
            'Points': 'Pts'
            }

    datos_ponderar = ['Minutes', 'PersonalFouls', 'Points']

    
    claves_2 = {
            'Name': 'Player', 'Minutes': 'Min',
            'Games': 'G', 'FieldGoalsPercentage': 'FG%',
            'FreeThrowsPercentage': 'FT%', 'ThreePointersPercentage': 'TP%',
            'TotalReboundsPercentage': 'Reb%',
            'PersonalFouls': 'Fouls', 'Points': 'Pts'
            }
    
    jugadores = {}
    jug_partido = {}
    for dato in claves_1.values():
        jugadores[dato] = []

    for dato in claves_2.values():
        jug_partido[dato] = []

    for jugador in team_stats:
        if jugador['Games'] != 0:
            for key, value in claves_1.items():
                jugadores[value].append(jugador[key])
            
            for key, value in claves_2.items():
                if key in datos_ponderar:
                    jug_partido[value].append(round(jugador[key]/partidos, 2))
                else:
                    jug_partido[value].append(jugador[key])

    df = pd.DataFrame(jugadores)
    df2 = pd.DataFrame(jug_partido)

    df_claves_1 = pd.DataFrame([claves_1]).transpose().rename(columns={0: 'Abreviacion'})
    df_claves_2 = pd.DataFrame([claves_2]).transpose().rename(columns={0: 'Abreviacion'})

    return [(df, df2), (df_claves_1, df_claves_2)]


def load(entrada: list or None):

    def imagen_tabla(df:pd.DataFrame, nombre: str, fontsize: int = 14):
        if not os.path.exists(f'./imagenes/{nombre}.png'):
            dfi.export(
                    df, f'./imagenes/{nombre}.png',
                    table_conversion='matplotlib', fontsize=fontsize
                    )

    def buscar_equipo(driver, equipo):

        conseguido = False
        pred = driver.find_elements_by_id('1x2wrap')
        divs = driver.find_elements_by_tag_name('div')
        string = ''
        for tmp in pred:
            id = tmp

        for div in divs:
            if div == id:
                pred2 = div.find_elements_by_tag_name('div')
                for div in pred2:
                    if re.search(equipo, div.text):
                        string += str(div.text)
                        pred3 = div.find_elements_by_tag_name('div')
                        i = 0
                        for div in pred3:
                            i += 1
                            if i == 2:
                                pred4 = div.find_elements_by_tag_name('div')
                                i = 0
                                for div in pred4:
                                    i += 1
                                    if i == 2:
                                        pred5 = div.find_elements_by_tag_name('span')
                                        for div in pred5:
                                            if re.search('green', div.get_attribute('class')):
                                                conseguido = True
                                                ganador = div.text
                                                break
                break

        if conseguido:
            lista = string.split('\n')
            if ganador == '1':
                respuesta = f'El ganador será {lista[2]}'
            elif ganador == '2':
                respuesta = f'El ganador será {lista[6]}'
            else:
                respuesta = 'El resultado será un empate'
            return f'El proximo partido es:\n{lista[0]}\n{lista[2]} vs {lista[6]}\n{respuesta}'
        
        else:
            return False
    
    dfs = entrada[0]
    claves = entrada[1]
    if dfs is None:
        print('Ha ocurrido un error')
        return

    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.headless = True
    options.add_argument("--window-size=1920x1080")
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    driver.get(URL)
    mayor = driver.find_element_by_xpath('//*[@id="logo-box"]/div[2]/a')
    mayor.click()
    pred = driver.find_elements_by_tag_name('a')
    link_bueno = False
    patron = f'https://www.sportytrader.es/pronosticos/[\w/\.\/-]*{team_actual.lower()}[\w/\.\/-]*'
    for lem in pred:
        link = re.search(patron, lem.get_attribute('href'))
        if link is not None:
            link_bueno = link.group()
            break

    if link_bueno:
        driver.get(link_bueno)
        pron = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[4]/section/main/div[7]')
        driver.maximize_window() 
        driver.execute_script("window.scrollBy(0,3500)","")
        print(pron.text)
        print(f'Para más información, vaya a {link_bueno}')
        ganador = f'{pron.text}\nPara más informacion, vaya a: {link_bueno}'
    
    else:
        ganador = buscar_equipo(driver, team_actual)
        if ganador:
            print(ganador)
        else:
            driver.quit()
            ganador = 'Lo sentimos, pero en estos momentos no disponemos de ninguna prediccion fiable.'
            print('Lo sentimos, pero en estos momentos no disponemos de ninguna prediccion fiable.')
            print(f'No obstante, puede ir a {URL} para ver los próximos partidos de la NBA')


    if not os.path.isdir('imagenes'):
        os.mkdir('imagenes')
        imagen = requests.get('https://www.logolynx.com/images/logolynx/44/445c6c3208d6ffd616803fa0308ed8b2.png')
        with open('./imagenes/logo.png', 'wb') as code:
            code.write(imagen.content)

    elif not os.path.exists('./imagenes/logo.png'):
        imagen = requests.get('https://www.logolynx.com/images/logolynx/44/445c6c3208d6ffd616803fa0308ed8b2.png')
        with open('./imagenes/logo.png', 'wb') as code:
            code.write(imagen.content)

    for index in range(len(dfs)):

        imagen_tabla(dfs[index], f'df{index}')

    for index in range(len(claves)):

        imagen_tabla(claves[index], f'leyenda{index}', 11)

    crear_presentacion(f'{team_actual}-{datetime.now().strftime("%d-%m-%Y")}', SEASON, ganador)
    nombres = ['df0.png', 'df1.png', 'leyenda0.png', 'leyenda1.png']
    for name in nombres:
        if os.path.exists(f'./imagenes/{name}'):
            os.remove(f'./imagenes/{name}')


def main():
    load(transform(extract()))


if __name__ == '__main__':

    main()