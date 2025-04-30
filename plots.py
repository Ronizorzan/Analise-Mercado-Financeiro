import plotly.express as px                                   
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd
import numpy as np
from streamlit import cache_resource


# Configurar o formato de números no estilo brasileiro (vírgula como separador decimal)


#Dicionário para Tradução das Colunas
traducao = {"Close": "Fechamento", "High": "Máxima", "Low": "Mínima", "Open": "Abertura", "Volume": "Volume de Negociações"}

@cache_resource
class Gerador_de_graficos:
    """Esta classe foi projetada para realizar a extração, processamento e permitir a visualização de dados financeiros de empresas específicas,
      utilizando a biblioteca yfinance. Ela permite realizar cálculos como variações percentuais, médias móveis e bandas de Bollinger,
      além de ajustar os dados com base em intervalos de tempo pre-definidos à medida que o intervalo de tempo escolhido pelo usuário aumenta.
      Além disso expansões, como novos cálculos e gráficos podem ser facilmente implementados de acordo com a necessidade de negócios, 
      sem que isso adicione qualquer complexidade adicional à classe ou às funções adicionais. """
    def __init__(self, data_inicio, data_final, empresa_selecionada):           
        empresas = {"Tesla": "TSLA", "General Motors": "GM", "Ford": "F", "Toyota": "TM", 
                        "Volkswagen": "VWAGY", "BYD": "BYDDF"} # Dicionário para mapeamento e filtragem das empresas
        self.data_inicio = data_inicio
        self.data_final = data_final
        self.empresa = empresa_selecionada
        if pd.to_datetime(data_inicio) > pd.to_datetime(data_final):
            raise ValueError("A data Inicial deve ser maior do que a data Final")
        self.dados = yf.download(empresas[empresa_selecionada], data_inicio, data_final, multi_level_index=False)
        self.dados = pd.DataFrame(self.dados)        
        self.dados.rename(columns=traducao, inplace=True)        
        
                        
        #Condição de Atualização dos gráficos de acordo com o intervalo de datas escolhido
        if self.dados.shape[0] >45 and self.dados.shape[0]<180:
            self.dados = self.dados.resample("W").last()
        elif self.dados.shape[0] >=180 and self.dados.shape[0] <500:
            self.dados = self.dados.resample("ME").last()
        elif self.dados.shape[0] >=500:
            self.dados = self.dados.resample("YE").last()

        self.dados.index.strftime('%d/%m/%y')

        
    def Gerador_de_calculos(self):        
        variacao_perc = self.dados["Fechamento"].pct_change()*100       #Variação Percentual das Ações              
        medias_moveis = (self.dados["Fechamento"].rolling(4).mean()) #Médias Móveis
        medias_moveis.bfill(inplace=True)
        medias_moveis_desv = self.dados["Fechamento"].rolling(4).std()
        self.dados["Banda Superior"] = (medias_moveis + (2 * medias_moveis_desv)).bfill() #Cálculos bandas de bollinger
        self.dados["Banda Inferior"] = (medias_moveis - (2 * medias_moveis_desv)).bfill()
        
                
        return self.dados, medias_moveis, variacao_perc
    
#Função para plotagem do gráfico de barras    
def Grafico_barras(dados, coluna):                    
    fig1 = px.bar(dados, x=dados.index.strftime("%d/%m/%y"), y=dados[coluna], color=dados[coluna],
                   color_continuous_scale=px.colors.sequential.Blues, title="Gráfico de Barras")
    fig1.update_layout(xaxis_title="Data", yaxis_title="Valor")                     
    return fig1


#Gráfico para plotagem das previsões futuras
def Grafico_linhas(dados, coluna):                     
    fig3 = px.line(dados, x=dados.index.strftime("%d/%m/%y"), y=dados[coluna])
    fig3.update_layout(xaxis_title="Data", yaxis_title="Valor das Ações", xaxis_rangeslider_visible=True)
    fig3.update_traces(text="Valor das Ações", textposition="top right", hovertemplate="Valor das Ações %{y}<br>Data: %{x}")
    return fig3

#Gráfico para plotagem comparativa (dados de teste, previsões)
def Grafico_linhas_previsoes(dados):                 
    fig3 = px.line(dados, x=dados["Date"], y=["Valores Reais", "Previsões"]
                   )
    fig3.update_layout(xaxis_title="Data", yaxis_title="Valor das Ações", xaxis_rangeslider_visible=True)
    fig3.update_traces(text="Valor das Ações", textposition="top right", hovertemplate="Valor das Ações %{y}<br>Data: %{x}")
    return fig3

#Função para plotagem do gráfico de Linhas
#Função substituida por Grafico_linhas_tendencia
def Grafico_linhas_values(dados):    
    fig4 = px.line(dados, x=dados.index.strftime("%d/%m/%y"), y=dados.values)
    fig4.update_layout(xaxis_title="Data", yaxis_title="Valor", yaxis=dict(titlefont=dict(size=16)))
    fig4.update_traces(text="Data", textposition="top left", hovertemplate="valor: %{y}<br>Data: %{x} ",
                       line=dict(color="#07B8FB", width=2), mode="lines")    
    return fig4


#Função para plotagem do gráfico de Velas
def Grafico_velas(dados):
    fig5 = go.Figure(data=[go.Candlestick(x=dados.index.strftime("%d/%m/%y"), open=dados["Abertura"], 
                                         close=dados["Fechamento"], low=dados["Mínima"], high=dados["Máxima"], whiskerwidth=0.0)])
    dados["Variacao"] = (dados["Fechamento"] - dados["Abertura"]).abs()  # Variação absoluta

    # Data e valor da maior variação positiva (quando Fechamento > Abertura)    
    dados_velas = dados.copy()

    # Formatar o índice para datas no formato "DD/MM/YY"
    dados_velas.index = dados_velas.index.strftime("%d/%m/%y")

    # Calcular a variação percentual prevenindo divisão por zero
    dados_velas["Porcentagem"] = dados_velas.apply(
        lambda row: ((row["Fechamento"] - row["Abertura"]) / row["Abertura"] * 100) if row["Abertura"] != 0 else 0,
        axis=1
    )
        
    # Processar a variação positiva (apenas onde Fechamento > Abertura)
    pos = dados_velas[dados_velas["Fechamento"] > dados_velas["Abertura"]]
    if not pos.empty:
        variacao_positiva_data = pos["Variacao"].idxmax()
        valor_variacao_positiva = pos["Variacao"].max()
        variacao_positiva_porc = pos["Porcentagem"].max()
    else:
        variacao_positiva_data = "N/A"
        valor_variacao_positiva = 0
        variacao_positiva_porc = 0

    # Processar a variação negativa (apenas onde Fechamento < Abertura)
    neg = dados_velas[dados_velas["Fechamento"] < dados_velas["Abertura"]]
    if not neg.empty:
        variacao_negativa_data = neg["Variacao"].idxmax()
        valor_variacao_negativa = neg["Variacao"].max()
        variacao_negativa_porc = neg["Porcentagem"].min()
    else:
        variacao_negativa_data = "N/A"
        valor_variacao_negativa = 0
        variacao_negativa_porc = 0       
                      
    # Gerar texto customizado para hover (Tradução)
    dados_velas.index = pd.to_datetime(dados_velas.index, dayfirst=True)
    hover_text = [
        f"Data: {index.strftime('%d/%m/%Y')}<br>"  # Formata a data para DD/MM/YYYY
        f"Abertura: {row['Abertura']:,.2f}<br>"
        f"Máxima: {row['Máxima']:,.2f}<br>"
        f"Mínima: {row['Mínima']:,.2f}<br>"
        f"Fechamento: {row['Fechamento']:,.2f}"
        for index, row in dados_velas.iterrows()
]

    fig5.update_traces(hovertext=hover_text, increasing=dict(line_color="green"), #Cor para alta
            decreasing=dict(line_color="red"), # Cor para baixa
             hoverinfo="text") # Usar o texto personalizado no hover
    
    fig5.update_layout(xaxis_title= f"Dia da Maior Variação Negativa: {variacao_negativa_data}<br>  Maior Variação Negativa: \
        <span style='color:red'>-${valor_variacao_negativa:,.2f}({variacao_negativa_porc:,.2f}%)</span>", #Formatação e estilização dos textos para variação negativa
                        title=f"Dia da Maior variação Positiva: {variacao_positiva_data}<br>Maior Variação Positiva: \
        <span style='color:green'>+${valor_variacao_positiva:,.2f}(+{variacao_positiva_porc:,.2f}%)</span>",  #Formatação e estilização dos textos para variação positiva
           yaxis_title="Valor das Ações", hoverlabel=dict(namelength=-1), hovermode="x unified", yaxis=dict(titlefont=dict(size=16), tickformat=",.2f"),
           xaxis_rangeslider_visible=False, xaxis=dict(type="category",tickmode="array", titlefont=dict(size=16))) 

    return fig5

#Função para plotagem do gráfico de bollinger
def Grafico_bollinger(dados):
    fig6 = px.line(dados, x=dados.index.strftime("%d/%m/%y"), y=["Fechamento", "Banda Superior", "Banda Inferior"],
                labels={"value": "Valor", "variable": "Indicador", "x":"Data"},
                title="Identifique momentos de variação nas compras e vendas")
    fig6.update_layout(xaxis_title="Data", yaxis_title="Valor das Ações", 
                       yaxis=dict(titlefont=dict(size=17), tickformat=",.2f")
                       )
    
    return fig6

# Função para separação dos dados para treino, teste e validação
def separa_dados(data, X, y):
    length_treino = int(len(data) * 0.75) # 75% para teste
    length_val = int(len(data) * 0.85)

    #Separação das variáveis independentes
    X_train = X[: length_treino] # Variáveis independentes treino
    X_val = X[length_treino: length_val] # Variáveis independentes validação
    X_test = X[length_val :]  # Variáveis independentes teste

    #Separação das variáveis dependentes
    y_train = y[: length_treino] # Variável dependente treino     
    y_val = y[length_treino: length_val] # Variável dependente validação
    y_test = y[length_val :]  # Variável dependente teste
    index_test = data.index[length_val :]
    
    return X_train, X_val, X_test, y_train, y_val, y_test, index_test[30:]

    


def Gerador_Previsoes_RN(horizonte, X_teste, modelo, scaler, passos=30):
    
    ultimo_dado = np.reshape(X_teste, (-1,1)) #Mudança de formato para o normalizador    
    ultimo_dado = ultimo_dado[-passos:]   #Filtro dos passos no tempo (30 últimos dados)
    ultimo_dado = scaler.transform(ultimo_dado)   #Normalização dos dados
    previsoes = []  #Lista para armazenamento das previsões
    
    #Loop para previsão, atualização dos dados e adição à lista
    for _ in range(horizonte):
        janela_dados = np.reshape(ultimo_dado, (1, passos, 1)) #Mudança para formato aceito pela rede neural 
        previsao = modelo.predict(janela_dados, verbose=0).flatten()[0] 
        previsoes.append(previsao) #Adição da previsão à lista
                
        ultimo_dado = np.append(ultimo_dado[1:], [[previsao]], axis=0) #Remoção do último dado e adição da previsão ao final
    previsoes = np.array(previsoes).reshape(-1,1)
    previsoes = scaler.inverse_transform(previsoes)  #Reversão da normalização
    return previsoes


# Função para gerar previsões para um horizonte definido a partir da última janela do conjunto de teste
#Função usada no próximo projeto com dados multivariados
def Gerador_Previsoes(horizonte, X_teste, modelo, scaler, passos=30):
    """Função adaptada para dados multivariados.
    Gera previsões para um horizonte definido a partir da última janela do conjunto de teste.
    Args:
        horizonte (int): Número de passos à frente para prever.
        X_teste (numpy.ndarray): Dados de teste com shape (n_samples, timesteps, n_features).
        modelo (keras.Model): Modelo treinado para fazer previsões.
        scaler (MinMaxScaler): Scaler usado para normalizar os dados.
        passos (int): Número de passos no tempo usados na janela deslizante.
    Returns:previsoes (numpy.ndarray): Previsões para o horizonte definido."""

    ultimo_dado = X_teste[-1, :, :]   # shape (timesteps, n_features)
    previsoes = []
    for _ in range(horizonte):
        janela_dados = ultimo_dado.reshape(1, passos, ultimo_dado.shape[1])
        previsao = modelo.predict(janela_dados, verbose=0)  # shape (1, 4)
        previsoes.append(previsao[0])
        ultimo_dado = np.vstack([ultimo_dado[1:], previsao])
    previsoes = np.array(previsoes)  # (horizonte, 4)
    previsoes = scaler.inverse_transform(previsoes)
    return previsoes


        
# Prepara os dados multivariados, criando janelas temporais
def prepara_dados(ready_data, timesteps=30):
    length = len(ready_data)
    independ = []
    depend = []
    for i in range(timesteps, length):
        independ.append(ready_data[i - timesteps: i,:])
        depend.append(ready_data[i,0])
    return np.array(independ), np.array(depend)


# Prepara os dados multivariados, criando janelas temporais
#Função usada no próximo projeto com dados multivariados
def prepara_dados_multivariada(ready_data, timesteps=30):
    X, y = [], []
    for i in range(timesteps, len(ready_data)):
        X.append(ready_data[i-timesteps:i, :])
        y.append(ready_data[i, :])
    return np.array(X), np.array(y)



# (c) Função de treinamento iterativo com Teacher Forcing + Scheduled Sampling  
def treinamento_iterativo(modelo, X_train, y_train, validation_data,  teacher_forcing_epochs, iterative_epochs, batch_size, sampling_rate=0.6):
    """
    Primeiro, treina com teacher forcing.
    Depois, na fase iterativa, para cada janela, com probabilidade sampling_rate usa a previsão.
    """
    print("Iniciando a fase de Teacher Forcing...")
    modelo.fit(X_train, y_train, validation_data= tuple(validation_data), epochs=teacher_forcing_epochs, batch_size=batch_size, verbose=1)
    
    print("Atualizando as entradas iterativamente com Scheduled Sampling...")
    X_train_iterativo = np.copy(X_train)
    timesteps = X_train_iterativo.shape[1]
    n_features = X_train_iterativo.shape[2]
    
    for i in range(X_train_iterativo.shape[0]):
        # Obtém a janela atual e faz a previsão
        entrada_atual = X_train_iterativo[i].reshape(1, timesteps, n_features)
        previsao = modelo.predict(entrada_atual, verbose=0)  # shape (1, n_features)
        # Scheduled sampling: com probabilidade sampling_rate, substitui a última linha da janela
        if np.random.rand() < sampling_rate:
            X_train_iterativo[i, -1, :] = previsao[0]
        # senão, mantém o valor real (já presente em X_train_iterativo)
    
    print("Treinando iterativamente com as janelas atualizadas...")
    modelo.fit(X_train_iterativo, y_train, validation_data= tuple(validation_data), epochs=iterative_epochs, batch_size=batch_size, verbose=1)
    
    return modelo




def Grafico_linhas_tendencia(dados, tendencia=False, legenda="Tendência", coluna="Fechamento"):    
    # Criação do gráfico original    
    dados = dados.reset_index()  # Reseta o índice para usá-lo como coluna
    dados['Data'] = dados["Date"].dt.strftime("%d/%m/%y")  # Converte o índice para string de data
    fig4 = px.line(
        dados, 
        x=dados["Data"], ## Usa a coluna 'Data' criada
        y=dados[coluna]  # Usa a coluna de valores
    )
    
    # Adicionando a linha de tendência
    #x_numerico = np.arange(dados.shape[0])  # Converter o índice para valores numéricos
    coef = np.polyfit(dados.index[:], dados[coluna].values, 1)  # Ajuste linear
    tendencia = np.poly1d(coef)  # Criação da equação da linha de tendência
    
    if tendencia:
        fig4.update_traces(
            text="Data", 
            textposition="top left", 
            hovertemplate="valor: %{y}<br>Data: %{x}",
            line=dict(color="#07B8FB", width=2)        
        )
    
        fig4.add_scatter(
            x=dados["Data"], 
            y=tendencia(dados.index[:]), 
            mode='lines', 
            name=legenda, 
            line=dict(color='white', dash='dash')
        )
        
        # Ajustando o layout e as propriedades
        fig4.update_layout(
            xaxis_title="Data", 
            yaxis_title="Valor", 
            yaxis=dict(titlefont=dict(size=16), tickformat=",.2f"),
            title="Gráfico com Linha de Tendência"
        )
    
    
    return fig4



