import sys
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import numpy as np
import time
from PyQt5 import QtWidgets, QtCore
from PyQt5 import QtWidgets, QtGui, QtCore



def load_player_data():
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Host': 'stats.nba.com',
        'Origin': 'https://www.nba.com',
        'Referer': 'https://www.nba.com/',
        'Sec-Ch-Ua': '"Not A;Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': 'Windows',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }

    df = pd.DataFrame()
    season_types = ['Regular%20Season', 'Playoffs']
    years = ['2023-24']
    begin_loop = time.time()

    for y in years:
        for s in season_types:
            api_url = f'https://stats.nba.com/stats/leagueLeaders?LeagueID=00&PerMode=PerGame&Scope=S&Season={y}&SeasonType={s}&StatCategory=PTS'
            response = requests.get(api_url, headers=headers)
            if response.status_code == 200:
                r = response.json()
                temp_df1 = pd.DataFrame(r['resultSet']['rowSet'], columns=r['resultSet']['headers'])
                temp_df2 = pd.DataFrame({'Year': [y for _ in range(len(temp_df1))], 
                                        'Season_type': [s.replace('%20', ' ') 
                                                        for _ in range(len(temp_df1))]})
                temp_df3 = pd.concat([temp_df2, temp_df1], axis=1)
                df = pd.concat([df, temp_df3], ignore_index=True)
                print(f"finished {y} {s.replace('%20', ' ')}")
            else:
                print(f"Failed to retrieve data for {y} {s.replace('%20', ' ')}: {response.status_code}")
            lag = np.random.uniform(low=5, high=40)
            print(f"...waiting {lag:.2f} seconds...")
            time.sleep(lag)   

    print(f"Processo completo em {time.time() - begin_loop:.2f} segundos.")
    return df
    # print(df.head())  # Mostra as primeiras linhas do DataFrame para diagnóstico
    # return df
def fetch_player_profile(player_id, player):
    player = player.replace(" ", "-")
    profile_url = f"https://www.nba.com/player/{player_id}/{player}/profile"
    player_info = ""

    response = requests.get(profile_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.select_one('#__next > div.Layout_base__6IeUC.Layout_justNav__2H4H0 > div.Layout_mainContent__jXliI > section > div.MaxWidthContainer_mwc__ID5AG.PlayerView_pvSection__whddS > section:nth-child(2) > div > div')
        
        if table:
            # Criando a tabela HTML
            html = "<table border='1' style='margin-left: auto; margin-right: auto;'>"
            for row in table.find_all('tr'):
                cells = row.find_all(['th', 'td'])
                row_str = "<tr>" + "".join(f"<td>{cell.get_text(strip=True)}</td>" for cell in cells) + "</tr>"
                html += row_str
            html += "</table>"
            player_info = html
            
            # Adicionando estatísticas resumidas
            data_element = soup.select('#__next > div.Layout_base__6IeUC.Layout_justNav__2H4H0 > div.Layout_mainContent__jXliI > section > div.PlayerSummary_summary__CGowU > section.PlayerSummary_summaryBot__D5ihs > div > div.PlayerSummary_statsSectionStats__9TdUC')
            abbr_mapping = {
                'PPG': 'PTS',
                'RPG': 'REB',
                'APG': 'AST',
                'PIE': 'IMPACTO JOGADOR'
            }
            stats_html = "<div>"
            for element in data_element:
                text = element.text
                matches = re.findall(r'([A-Z]+)(\d+\.\d+)', text)
                for match in matches:
                    stat, value = match
                    stats_html += f"<p>{abbr_mapping.get(stat, stat)}: {value}</p>"
            stats_html += "</div>"
            player_info += stats_html
        else:
            player_info = "Tabela não encontrada na página."
    else:
        player_info = f"Falha na solicitação: {response.status_code}"

    return player_info



class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.dados = load_player_data()
        self.init_ui()     
    


    def init_ui(self):
        self.layout = QtWidgets.QVBoxLayout()
        self.team_filter = QtWidgets.QComboBox(self)
        self.team_filter.addItems(["All Teams"] + list(set(self.dados['TEAM'].values)))
        self.team_filter.currentIndexChanged.connect(self.update_listbox)
        self.layout.addWidget(self.team_filter)

        self.listbox = QtWidgets.QListWidget(self)
        self.listbox.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.listbox.currentItemChanged.connect(self.on_select)
        self.layout.addWidget(self.listbox)
             

        self.stats_text_widget = QtWidgets.QTextEdit(self)
        self.stats_text_widget.setReadOnly(True)
        self.layout.addWidget(self.stats_text_widget)
        self.setLayout(self.layout)
        self.setWindowTitle("Seleção de Jogador da NBA")
        # self.resize(500, 600)

    def update_listbox(self, index):
        team_name = self.team_filter.itemText(index)
        self.listbox.clear()
        if team_name == "All Teams":
            for index, row in self.dados.iterrows():
                self.listbox.addItem(f"{row['PLAYER']} ({row['TEAM']})")
        else:
            filtered_data = self.dados[self.dados['TEAM'] == team_name]
            for index, row in filtered_data.iterrows():
                self.listbox.addItem(f"{row['PLAYER']} ({row['TEAM']})")

    def on_select(self, current, previous):
        if current:
            player_info = current.text().split(' (')
            if len(player_info) > 1:
                player_name, player_team = player_info[0], player_info[1].rstrip(')')
                player_id = self.dados.loc[self.dados['PLAYER'] == player_name, 'PLAYER_ID'].iloc[0]
                profile_info = fetch_player_profile(player_id, player_name)
                self.stats_text_widget.setHtml(profile_info)  # Usando setHtml para renderizar o HTML
    def on_team_selected(self, index):
        team = self.team_filter.itemText(index)
        self.update_ui(team)
        
   

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())