from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import time
import re
import json
import csv

def append_list_as_row(file_name, list_of_elem):
    with open(file_name, 'a+', newline='') as write_obj:
        csv_writer = csv.writer(write_obj, delimiter=";")
        csv_writer.writerow(list_of_elem)

def get_links(driver):
    links = []
    info_elements = driver.find_elements_by_xpath("//a[contains(@href, 'matches') and contains(@title, 'Saiba')]")
    for element in info_elements:
        links.append(element.get_attribute('href'))
    return links

def click_previous_button(driver):
    previous_buttons = driver.find_elements_by_class_name("previous ")
    driver.execute_script("arguments[0].click();", previous_buttons[0])
    time.sleep(3)

def check_previous_disabled(driver):
    print(len(driver.find_elements_by_xpath("//a[contains(@rel, 'previous') and contains(@class, 'disabled')]")))
    if len(driver.find_elements_by_xpath("//a[contains(@rel, 'previous') and contains(@class, 'disabled')]")) != 0:
        return True
    else:
        return False

def get_links_of_competition(competition_url):
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(competition_url)
    time.sleep(2)
    links = []

    while True:
        links.append(get_links(driver))
        if not check_previous_disabled(driver):
            click_previous_button(driver)
        else:
            driver.quit()
            flat_links = [item for sublist in links for item in sublist]
            return flat_links

def get_match_links(competitions):
    links = []
    for year, url in competitions.items():
        print("Proccesing {} : {}". format(year, url))
        links.append(get_links_of_competition(url))


    flat_links = [item for sublist in links for item in sublist]

    return flat_links

def process_match(match, output):
    page = requests.get(match)
    soup = BeautifulSoup(page.content, 'html.parser')

    main_info = soup.find('div', id="page_match_1_block_match_info_5")
    time_casa = main_info.find('div', class_="container left").find('h3', class_='thick').find('a').string
    time_fora = main_info.find('div', class_="container right").find('h3', class_='thick').find('a').string

    details_clearfix = soup.find_all('div', class_='details clearfix')

    ano = details_clearfix[0].find_all("dd")[0].string
    rodada = details_clearfix[0].find_all("dd")[2].string
    data_do_jogo = details_clearfix[0].findAll("span", {"class": "timestamp"})[0].string
    horário_do_jogo = details_clearfix[0].findAll("span", {"class": "timestamp"})[1].string
    ano = data_do_jogo[-4:]
    placar = ''.join(soup.find('div', class_='container middle').find('h3').string.split())

    local = details_clearfix[2].find_all("dd")[0].string
    publico = details_clearfix[2].find_all("dd")[1].string

    cartões_amarelos_casa = 0
    cartões_amarelos_fora = 0
    cartões_vermelhos_casa = 0
    cartões_vermelhos_fora = 0

    imgs_1 = soup.find_all('table', class_='playerstats lineups table')[0].find_all('img')
    imgs_2 = soup.find_all('table', class_='playerstats lineups table')[1].find_all('img')
    imgs_3 = soup.find_all('table', class_='playerstats lineups substitutions table')[1].find_all('img')
    imgs_4 = soup.find_all('table', class_='playerstats lineups substitutions table')[1].find_all('img')

    for img in imgs_1:
        if img['src'] == 'https://s1.swimg.net/gsmf/819/img/events/YC.png':
            cartões_amarelos_casa += 1
        if img['src'] == 'https://s1.swimg.net/gsmf/819/img/events/Y2C.png':
            cartões_vermelhos_casa += 1
        if img['src'] == 'https://s1.swimg.net/gsmf/819/img/events/RC.png':
            cartões_vermelhos_casa += 1

    for img in imgs_2:
        if img['src'] == 'https://s1.swimg.net/gsmf/819/img/events/YC.png':
            cartões_amarelos_fora += 1
        if img['src'] == 'https://s1.swimg.net/gsmf/819/img/events/Y2C.png':
            cartões_vermelhos_fora += 1
        if img['src'] == 'https://s1.swimg.net/gsmf/819/img/events/RC.png':
            cartões_vermelhos_fora += 1

    for img in imgs_3:
        if img['src'] == 'https://s1.swimg.net/gsmf/819/img/events/YC.png':
            cartões_amarelos_casa += 1
        if img['src'] == 'https://s1.swimg.net/gsmf/819/img/events/Y2C.png':
            cartões_vermelhos_casa += 1
        if img['src'] == 'https://s1.swimg.net/gsmf/819/img/events/RC.png':
            cartões_vermelhos_casa += 1

    for img in imgs_4:
        if img['src'] == 'https://s1.swimg.net/gsmf/819/img/events/YC.png':
            cartões_amarelos_fora += 1
        if img['src'] == 'https://s1.swimg.net/gsmf/819/img/events/Y2C.png':
            cartões_vermelhos_fora += 1
        if img['src'] == 'https://s1.swimg.net/gsmf/819/img/events/RC.png':
            cartões_vermelhos_fora += 1

    page_commentary = requests.get(match + 'commentary/')
    soup_commentary = BeautifulSoup(page_commentary.content, 'html.parser')

    iframe = soup_commentary.find_all('iframe')[1]
    stats_url = 'https://br.soccerway.com/' + iframe['src']

    stats_page = requests.get(stats_url)
    stats_soup = BeautifulSoup(stats_page.content, 'html.parser')

    chutes_a_gol_casa = stats_soup.find_all('tr')[5].find('td', class_="legend left value").string
    chutes_a_gol_fora = stats_soup.find_all('tr')[5].find('td', class_="legend right value").string
    chutes_para_fora_do_gol_casa = stats_soup.find_all('tr')[7].find('td', class_="legend left value").string
    chutes_para_fora_do_gol_fora = stats_soup.find_all('tr')[7].find('td', class_="legend right value").string

    javascript = stats_soup.find_all('script', type="text/javascript")[7]

    s = javascript.string

    # Parsing fora
    start = '{"name":'
    end = ',{'
    s = s[s.find(start)+len(start):s.rfind(end)]
    start = '"y":'
    end = '}'
    posse_de_bola_fora = s[s.find(start)+len(start):s.rfind(end)]

    # Parsing casa
    s = javascript.string
    start = ',{"name":'
    end = '}'
    s = s[s.find(start)+len(start):s.rfind(end)]
    start = '"y":'
    end = ',"'
    posse_de_bola_casa = s[s.find(start)+len(start):s.rfind(end)]

    row = [ano,
            rodada,
            time_casa,
            time_fora,
            placar,
            local,
            data_do_jogo,
            horário_do_jogo,
            publico,
            posse_de_bola_casa,
            posse_de_bola_fora,
            cartões_amarelos_casa,
            cartões_amarelos_fora,
            cartões_vermelhos_casa,
            cartões_vermelhos_fora,
            chutes_a_gol_casa,
            chutes_a_gol_fora,
            chutes_para_fora_do_gol_casa,
            chutes_para_fora_do_gol_fora]
    print(row)
    append_list_as_row(output, row)

if __name__ == '__main__':
    headers = ['ano',
            'rodada',
            'time_casa',
            'time_fora',
            'placar',
            'local',
            'data_do_jogo',
            'horário_do_jogo',
            'publico',
            'posse_de_bola_casa',
            'posse_de_bola_fora',
            'cartões_amarelos_casa',
            'cartões_amarelos_fora',
            'cartões_vermelhos_casa',
            'cartões_vermelhos_fora',
            'chutes_a_gol_casa',
            'chutes_a_gol_fora',
            'chutes_para_fora_do_gol_casa',
            'chutes_para_fora_do_gol_fora']

    competitions_dict = {2012 : 'https://br.soccerway.com/national/brazil/serie-a/2012/regular-season/r17449/matches/',
                            2013 : 'https://br.soccerway.com/national/brazil/serie-a/2013/regular-season/r20935/matches/',
                            2014 : 'https://br.soccerway.com/national/brazil/serie-a/2014/regular-season/r24110/matches/',
                            2015 : 'https://br.soccerway.com/national/brazil/serie-a/2015/regular-season/r30889/matches/',
                            2016 : 'https://br.soccerway.com/national/brazil/serie-a/2016/regular-season/r34827/matches/',
                            2017 : 'https://br.soccerway.com/national/brazil/serie-a/2017/regular-season/r39899/matches/',
                            2018 : 'https://br.soccerway.com/national/brazil/serie-a/2018/regular-season/r45710/matches/',
                            2019 : 'https://br.soccerway.com/national/brazil/serie-a/2019/regular-season/r51143/matches/'
                            }

    years = [2019]

    for year in years:
        competitions = {year : competitions_dict[year]}
        matches = get_match_links(competitions)
        append_list_as_row('data/' + str(year) + '_matches.csv', matches)
        append_list_as_row('data/' + str(year) + '_data.csv', headers)
        print('Number of matches: {}'.format(len(matches)))
        for match in matches:
            try:
                process_match(match, 'data/' + str(year) + '_data.csv')
            except:
                append_list_as_row('data/failed.csv', [match])
