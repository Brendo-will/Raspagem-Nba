# Raspagem-Nba

Um projeto que envolve coletar e exibir dados de jogadores da NBA utilizando uma interface gráfica. Ele está estruturado em duas partes principais: funções de back-end para coletar dados e uma classe de interface gráfica para apresentar esses dados. 

## 1. Coleta de Dados (load_player_data e fetch_player_profile)

load_player_data(): Coleta dados de desempenho dos jogadores da NBA para as temporadas regulares e playoffs de 2023-24. Utiliza a API oficial da NBA com headers específicos para simular um navegador. 

Os dados são agregados em um DataFrame do pandas. Além disso, inclui um mecanismo de espera entre as solicitações para evitar o bloqueio por excesso de requisições.

fetch_player_profile(player_id, player): Obtém e formata informações do perfil de um jogador específico, raspando dados de uma página HTML usando BeautifulSoup. 

Extrai informações de tabelas e de seções de resumo de estatísticas, convertendo-as em formato HTML para exibição.

## 2. Interface Gráfica (MainWindow)

A classe MainWindow gerencia a interface gráfica, permitindo que o usuário selecione uma equipe e visualize informações detalhadas dos jogadores dessa equipe.

init_ui(): Configura os elementos visuais da janela principal, como combobox para seleção de equipes e uma área de texto para exibir as informações do jogador selecionado.
update_listbox(): Atualiza a lista de jogadores com base na equipe selecionada.

on_select(): Método chamado quando um jogador é selecionado, responsável por buscar e exibir as informações detalhadas do jogador.


## Possíveis Melhorias
Cache de Dados: Implementar um sistema de cache para os dados dos jogadores poderia melhorar a performance, evitando requisições repetidas à mesma informação.

Paralelização: Paralelizar as requisições de dados para diferentes anos ou tipos de temporada poderia acelerar significativamente o processo de coleta de dados.

Melhoria na UI: Adicionar mais funcionalidades na interface, como filtros por jogador, visualizações gráficas das estatísticas, e melhor gestão do layout.

