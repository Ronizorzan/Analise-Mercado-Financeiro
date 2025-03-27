Aplicação para análise de Mercado Financeiro com gráficos automáticos e intuitivos destacando pontos relevantes de dados de ações de algumas empresas.

A aplicação é bastante customizável e dinâmica possibilitando o download de dados diretamente da API do Yahoo Fynance, visualização de gráficos de velas, gráficos estatísticos e gráficos de barras.

Além disso é disponibilizado um modelo de redes neurais para previsões de ações da empresa Tesla. 

O modelo foi desenvolvido utilizando uma abordagem de modelagem preditiva que une o poder das Redes Convolucionais (CNN) e das LSTM, 
permitindo a extração de padrões locais e a modelagem de dependências temporais dos dados históricos. Em alto nível, essa metodologia passa por duas fases:

Treinamento com Dados Reais (Teacher Forcing): Inicialmente, o modelo é treinado utilizando inputs reais para garantir que aprenda os padrões essenciais do comportamento do mercado. 
Essa fase estabelece uma base sólida onde o modelo se ajusta aos dados históricos com precisão.

Treinamento Iterativo com Previsões Próprias: Após a fase inicial, o modelo passa a incorporar suas próprias previsões como parte dos dados de entrada.
Essa estratégia, conhecida como treinamento iterativo, simula o cenário de previsão multi-passo – isto é, prever além do período com dados efetivos – e ajuda a mitigar o acúmulo de erros em previsões futuras.

Essa combinação robusta permite que o painel forneça previsões de alta confiabilidade. Indicadores de desempenho, como o RMSE (Root Mean Squared Error) de 25.51,
demonstram que o modelo mantém uma precisão consistente, mesmo ao extrapolar para períodos onde não há dados reais.

Em resumo, a confiança na previsão obtida se apoia em um processo meticuloso que une aprendizado com dados reais e adaptação progressiva às condições futuras. 
Essa abordagem integrada torna nossas previsões uma ferramenta sólida e informada para auxiliar na tomada de decisões no mercado financeiro.