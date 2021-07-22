from pandas.core.indexes.base import Index
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

def matchScraping(player_id_link):
    ############ SCRAPING DAS PARTIDAS ##############
    #1. Pegar conteudo HTML a partir da URL
    url = player_id_link

    option = Options()
    option.headless = True
    driver = webdriver.Firefox(options=option)
    print(url)
    
    driver.get(url)

    element_match = driver.find_element_by_xpath("//div[@class='main']")
    html_content_match = element_match.get_attribute('outerHTML')

    #2. Parsear o conteudo HTML Beautiful Soup
    soup = BeautifulSoup(html_content_match, 'html.parser')
    table = soup.find(name='table')
    player_deck = soup.find(class_='deck')
    player_deck = player_deck.get('title')

    title = soup.find_all('td',{'title': True})

    decks = []

    for repElem in title:
        repElemTitle = repElem.get('title')
        decks.append(repElemTitle)


    #3. Estruturar conteúdo em um Data Frame - Pandas
    #estruturando os data frames
    df_decks = pd.DataFrame(decks)
    df_full = pd.read_html(str(table))[0]
    df_results = df_full.iloc[:, [1]]
    df_results.columns= ['resultado']

    #droppando fases do torneio da lista de resultados
    indexFases = df_results[ df_results['resultado'] == 'Top 4 Cut'].index
    df_results = df_results.drop(indexFases)

    indexFases = df_results[ df_results['resultado'] == 'Phase 2'].index
    df_results = df_results.drop(indexFases)

    indexFases = df_results[ df_results['resultado'] == 'Phase 1'].index
    df_results = df_results.drop(indexFases)

    df_results = df_results.reset_index(drop=True)

    #concatenando e renomeando as colunas
    df = pd.concat([df_results, df_decks], axis=1, join="inner")

    df.columns= ['resultados', 'deck_adversário']

    #4. Converter o Data Frame para a formatação desejada 

    def converter_resultado(result,deck):
        if result == 'LOSS':
            return deck
        else:
            return player_deck

    def converter_ad(result,deck):
        if result != player_deck:
            return player_deck
        else:
            return deck 

    df['resultados'] = df.apply(lambda x: converter_resultado(x['resultados'],x['deck_adversário']), axis=1)
    df['deck_adversário'] = df.apply(lambda x: converter_ad(x['resultados'],x['deck_adversário']), axis=1)

    df.columns= ['vencedor', 'perdedor']

    driver.quit()
    return df


############ SCRAPING DOS CAMPEONATOS ##############

############ SCRAPING DOS PLAYERS ##############
# 1. Pegar conteudo HTML a partir da URL
url_players = "https://play.limitlesstcg.com/tournament/chill-37/standings"

option = Options()
option.headless = True
driver = webdriver.Firefox(options=option)

driver.get(url_players)

element = driver.find_element_by_xpath("//div[@class='standings completed']//table")
html_content = element.get_attribute('outerHTML')

# 2. Parsear o conteudo HTML Beautiful Soup
soup = BeautifulSoup(html_content, 'html.parser')
table = soup.find_all('a')

players = []

for player in table:
    repElemPlayer = player.get('href')
    if ("/player/" in player.get('href')) and ("/decklist" not in player.get('href')):
        repElemPlayer = player.get('href')
        players.append(repElemPlayer)

# 3. Estruturar conteúdo em um Data Frame - Pandas
df_players = pd.DataFrame(players)
df_players.columns = ['player_links']
df_csv = pd.DataFrame()

""" pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1) """
x=0
while x < len(df_players['player_links']):
    for player in df_players:
        df = matchScraping("https://play.limitlesstcg.com"+df_players['player_links'].values[x])
        df_csv = pd.concat([df_csv, df])
    x = x +1

#5. Exportar para um arquivo CSV
df_csv.to_csv("matchs.csv")
driver.quit()