# Importando as Bibliotecas
import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(layout = 'wide') # Colocando a configuração wide como padrão no aplicativo

def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor <1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000 
    return f'{prefixo} {valor:.2f} milhões'   

# Adicionando um Título ao Aplicativo
st.title('DASHBOARD DE VENDAS :shopping_trolley:') # shopping trolley é o nome do emoji de carrinho de compras

# Leitura dos Dados Através da API
url = 'https://labdados.com/produtos'
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']

st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Região', regioes)

if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True)
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

query_string = {'regiao': regiao.lower(), 'ano': ano}
response = requests.get(url, params = query_string) # Requisição dos dados
dados = pd.DataFrame.from_dict(response.json()) # from_dict é o método que transforma o json em dataframe
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y') # Convertendo dados de texto de 'Data da Compra' para o formato datetime

filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

## Tabelas
### Tabelas de Receita

# Tabela do Gráfico de Mapa
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

# Tabela do Gráfico de Linhas
receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year  # Transformando a data com informação de ano e armazenando em uma coluna
receita_mensal['Mês'] = receita_mensal['Data da Compra'].dt.month_name() 

# Tabela do Gráfico de Barras 
receita_categoria = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

### Tabelas Quantidade de Vendas

# Tabela Gráfico de Mapas
vendas_por_estado = dados.groupby('Local da compra')[['Preço']].count()
vendas_por_estado = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(vendas_por_estado, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending= False)

# Tabela Gráfico de Linhas
vendas_mensais = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].count().reset_index()
vendas_mensais['Ano'] = vendas_mensais['Data da Compra'].dt.year
vendas_mensais['Mês'] = vendas_mensais['Data da Compra'].dt.month_name()

# Tabela Gráfico de Barras
top_cinco_estados = dados.groupby('Local da compra')[['Preço']].count().sort_values('Preço', ascending = True).head()

# Tabela de Barra (Quantidade Vendas por Categoria)
vendas_categoria = dados.groupby('Categoria do Produto')[['Preço']].count().sort_values('Preço', ascending = True)


### Tabelas Vendedores
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count'])) # OBS: O gráfico desta tabela precisa ser criado diretamente na aba 3, pois foi criado um input de quantidade de vendedores. Usaremos o input para criar o gráfico.


## Gráficos

### Gráficos Aba 1 (Receita)

# Inserindo um Gráfico de Mapa
fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  size = 'Preço',
                                  template = 'seaborn',
                                  hover_name = 'Local da compra',
                                  hover_data = {'lat': False, 'lon': False},
                                  title = 'Receita Por Estado')


# Inserindo um Gráfico de Linhas
fig_receita_mensal = px.line(receita_mensal,
                            x = 'Mês',
                            y = 'Preço',
                            markers = 'True', # Adiciona um marcador na linha, identificando o valor do mês
                            range_y = (0, receita_mensal.max()), # Informa que o gráfico precisa iniciar do valor "0" ao invés dos valores da tabela
                            color = 'Ano', # Altera a cor da linha, de acordo com o ano
                            line_dash = 'Ano', # Altera o formato da linha, de acordo com o ano
                            title = 'Receita Mensal')

fig_receita_mensal.update_layout(yaxis_title = 'Receita') # Alterando o label do eixo y

# Inserindo o Gráfico de Barras Receita por Estado
fig_receita_estados = px.bar(receita_estados.head(),    # head para mostrar apenas os 5 primeiros estados
                            x = 'Local da compra',
                            y = 'Preço',
                            text_auto = True,  # Parâmetro para indicar que o valor deve constar em cima de cada uma das colunas, de forma automática
                            title = 'Top Estados (Receita)')  

fig_receita_estados.update_layout(yaxis_title = 'Receita') # Altera o label do eixo y

# Inserindo o Gráfico de Barras Receita por Categoria

fig_receita_categoria = px.bar(receita_categoria, # OBS: Não é necessário passar o 'x' e o 'y', porque a tabela só contém estas duas informações. O sistema já reconhece.
                               text_auto = True,
                               title = 'Receita Por Categoria')

fig_receita_categoria.update_layout(yaxis_title = 'Receita')


### Gráficos Aba 2 (Quantidade Vendas)

# Inserindo um Gráfico de Mapa
fig_mapa_vendas =  px.scatter_geo(vendas_por_estado,
                                 lat = 'lat',
                                 lon = 'lon',
                                 scope = 'south america',
                                 size = 'Preço',
                                 template = 'seaborn',
                                 hover_name = 'Local da compra',
                                 hover_data = {'lat': False, 'lon': False},
                                 title = 'Vendas Por Estado')



# Inserindo um Gráfico de Linhas
fig_vendas_mensais = px.line(vendas_mensais,
                            x = 'Mês',
                            y = 'Preço',
                            markers = True,
                            range_y = (0, vendas_mensais.max()),
                            color = 'Ano',
                            line_dash = 'Ano',
                            title = 'Quantidade Vendas Mensais') 

fig_vendas_mensais.update_layout(yaxis_title = 'Quantidade de Vendas')


# Inserindo um Gráfico de Barras
fig_top_cinco_estados = px.bar(top_cinco_estados,
                              text_auto = True,
                              title = 'Top 5 Estados (Qtd Vendas)')

fig_top_cinco_estados.update_layout(yaxis_title = 'Quantidade de Vendas')


# Inserindo um Gráfico de Barras por Categoria do Produto
fig_vendas_categoria = px.bar(vendas_categoria,
                             text_auto = True,
                             title = 'Vendas Por Categoria')

fig_vendas_categoria.update_layout(showlegend = False, yaxis_title = 'Quantidade de Vendas')



## Visualização com Streamlit (Inserindo os Gráficos no Aplicativo)

# Construindo as Abas
aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de Venda', 'Vendedores'])

with aba1:
# Adicionando Métricas e Colunas Dentro da Aba1
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width = True)  # O use_container_width mantém a medida do gráfico proporcional à coluna que ele está inserido.
        st.plotly_chart(fig_receita_estados, use_container_width = True)
    with coluna2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width = True)
        st.plotly_chart(fig_receita_categoria, use_container_width = True)
with aba2:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_vendas, user_containers_width = True)
        st.plotly_chart(fig_top_cinco_estados, user_containers_width = True)
       
    with coluna2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_mensais, user_containers_width = True)
        st.plotly_chart(fig_vendas_categoria, user_containers_width = True)
with aba3:
    qtd_vendedores = st.number_input('Quantidade de Vendedores', 2, 10, 5)  # number_input é um elemento interativo que pode ser adicionado no aplicativo
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores),
                                        x = 'sum',
                                        y = vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores).index, # Seleciona o nome dos vendedores
                                        text_auto = True, # Inclui o valor da receita em cada uma das barras
                                        title = f'Top {qtd_vendedores} Vendedores (Receita)')
        st.plotly_chart(fig_receita_vendedores)
       
    with coluna2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0]))
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores),
                                        x = 'count',
                                        y = vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores).index, # Seleciona o nome dos vendedores
                                        text_auto = True, # Inclui o valor da receita em cada uma das barras
                                        title = f'Top {qtd_vendedores} Vendedores (Quantidade de Vendas)')
        st.plotly_chart(fig_vendas_vendedores)