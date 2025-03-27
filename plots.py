import plotly.express as px                                   
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd
import numpy as np


# Configurar o formato de números no estilo brasileiro (vírgula como separador decimal)


#Dicionário para Tradução das Colunas
traducao = {"Close": "Fechamento", "High": "Máxima", "Low": "Mínima", "Open": "Abertura", "Volume": "Volume de Negociações"}


class Gerador_de_graficos:
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
            self.dados = self.dados.resample("W").mean()
        elif self.dados.shape[0] >=180 and self.dados.shape[0] <500:
            self.dados = self.dados.resample("MS").mean()
        elif self.dados.shape[0] >=500:
            self.dados = self.dados.resample("YE").mean()

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
    fig1 = px.bar(dados, x=dados.index.strftime("%d/%m/%y"), y=dados[coluna])
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
def Grafico_linhas_values(dados):    
    fig4 = px.line(dados, dados.index.strftime("%d/%m/%y"), dados.values)
    fig4.update_layout(xaxis_title="Data", yaxis_title="Valor", yaxis=dict(titlefont=dict(size=16 ), tickformat=",.2f"))
    fig4.update_traces(text="Data", textposition="top left", hovertemplate="valor: %{y}<br>Data: %{x} ")
    return fig4


#Função para plotagem do gráfico de Velas
def Grafico_velas(dados):
    fig5 = go.Figure(data=[go.Candlestick(x=dados.index.strftime("%d/%m/%y"), open=dados["Abertura"], 
                                         close=dados["Fechamento"], low=dados["Mínima"], high=dados["Máxima"], whiskerwidth=0.0)])
    dados["Variacao"] = (dados["Fechamento"] - dados["Abertura"]).abs()  # Variação absoluta

    # Data e valor da maior variação positiva (quando Fechamento > Abertura)    
    dados_velas = dados.copy()
        
    dados_velas.index = dados_velas.index.strftime("%d/%m/%y")          # Formatar a data para o estilo DD/MM/AAAA                                
    variacao_positiva_data = dados_velas.loc[dados_velas["Fechamento"] > dados_velas["Abertura"], "Variacao"].idxmax()    
    valor_variacao_positiva = dados_velas.loc[dados_velas["Fechamento"] > dados_velas["Abertura"], "Variacao"].max()

    #Variação Percentual
    dados_velas["Porcentagem"] = ((dados_velas["Fechamento"] - dados_velas["Abertura"]) / dados_velas["Abertura"]) *100
    variacao_positiva_porc = dados_velas["Porcentagem"].max()
    variacao_negativa_porc = dados_velas["Porcentagem"].min()

        
    
    # Data e valor da maior variação negativa (quando Fechamento < Abertura)
    variacao_negativa_data = dados_velas.loc[dados_velas["Fechamento"] < dados_velas["Abertura"], "Variacao"].idxmax()     
    valor_variacao_negativa = dados_velas.loc[dados_velas["Fechamento"] < dados_velas["Abertura"], "Variacao"].max()   
    
       
                      
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


        
# Função para preparação dos dados
def prepara_dados(ready_data, timesteps=30):
    length = len(ready_data)
    independ = []
    depend = []
    for i in range(timesteps, length):
        independ.append(ready_data[i - timesteps: i,0])
        depend.append(ready_data[i,0])
    return np.array(independ), np.array(depend)







