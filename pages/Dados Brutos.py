import streamlit as st
import requests 
import pandas as pd

@st.cache_data
def converte_csv(df):
    return df.to_csv(index = False).encode('utf-8')

def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso!', icon = "✅")
    time.sleep(5)
    sucesso.empty()

st.title('DADOS BRUTOS')

url = 'https://labdados.com/produtos'
response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as Colunas', list(dados.columns), list(dados.columns))

st.sidebar.title('Filtros')
with st.sidebar.expander('Nome do Produto'):
    produtos = st.multiselect('Selecione os Produtos', dados['Produto'].unique(), dados['Produto'].unique())
with st.sidebar.expander('Categoria do Produto'):
    categoria = st.multiselect('Selecione a categoria', dados['Categoria do Produto'].unique(), dados['Categoria do Produto'].unique())
with st.sidebar.expander('Preço do Produto'):
    preco = st.slider('Selecione o Preço', 0, 5000, (0,5000)) # (0,5000) Define um intervalo (tuple) como valor padrão 
with st.sidebar.expander('Frete da Venda'):
    frete = st.slider('Selecione o Frete', 0, 5000, (0,5000))
with st.sidebar.expander('Data da Compra'):
    data_compra = st.date_input('Selecione a data', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))
with st.sidebar.expander('Vendedor'):
    vendedor = st.multiselect('Selecione o Vendedor', dados['Vendedor'].unique(), dados['Vendedor'].unique())
with st.sidebar.expander('Local da Compra'):
    local = st.selectbox('Selecione o Local', dados['Local da compra'].unique())
with st.sidebar.expander('Avaliação da Compra'):
    avaliacao = st.slider('Selecione uma avaliação', 1, 5, (1,5))
with st.sidebar.expander('Tipo de Pagamento'):
    pagamento = st.multiselect('Selecione o Tipo de Pagamento', dados['Tipo de pagamento'].unique(), dados['Tipo de pagamento'].unique())
with st.sidebar.expander('Quantidade de Parcelas'):
    parcela = st.number_input('Escolha a Quantidade', min_value=1, max_value=24, value=1, step=1)




query = "`Produto` in @produtos & `Categoria do Produto` in @categoria & @preco[0] <= `Preço` <= @preco[1] & @frete[0] <= `Frete` <= @frete[1] & @data_compra[0] <=`Data da Compra` <= @data_compra[1] & `Vendedor` in @vendedor & `Local da compra` == @local & @avaliacao[0] <= `Avaliação da compra` <= @avaliacao[1] & `Tipo de pagamento` in @pagamento & @parcela <= `Quantidade de parcelas`"

dados_filtrados = dados.query(query)
st.dataframe(dados_filtrados)

st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas')

st.markdown('Escreva um nome para o arquivo')
coluna1, coluna2 = st.columns(2)
with coluna1:
    nome_arquivo = st.text_input('', label_visibility = 'collapsed', value = 'dados')
    nome_arquivo += '.csv'
with coluna2:
    st.download_button('Fazer o download da tabela em CSV', data = converte_csv(dados_filtrados), file_name = nome_arquivo, mime = 'text/csv', on_click = mensagem_sucesso)
