📈 Simulador de Precificação de Frete com Regressão Linear


Modelo simples que aprende, a partir de um histórico de cotações, quanto um frete "deveria" custar e aponta as cotações cujo preço cobrado ficou muito longe desse valor esperado.

⚠️ Projeto educacional. O histórico de 240 cotações é 100% fictício e não representa preços de mercado.

Por que este projeto existe?

Ao receber uma cotação de frete, a pergunta prática é: esse preço faz sentido para essa carga? Este simulador responde com um preço de referência calculado a partir de cotações anteriores e marca para revisão os casos que fogem do padrão, sem afirmar automaticamente que estão errados.

Objetivos
Aplicar uma regressão linear básica com variáveis numéricas (peso, distância) e categóricas (tipo de carga, modal, transportadora).
Comparar o preço cobrado com o preço estimado pelo modelo.
Sinalizar cotações que merecem revisão.
Gerar indicadores simples para avaliar a qualidade do modelo.
Dados
Coluna	Descrição
peso_kg	Peso da carga, em kg
distancia_km	Distância estimada, em km
tipo_carga	Geral, Refrigerada, Perigosa ou Frágil
modal	Rodoviário, Aéreo ou Marítimo
transportadora	Nome da transportadora (fictícia)
preco_cobrado_brl	Preço cobrado, em reais
Como funciona

Em uma frase: a regressão linear encontra a "regra média" que liga peso, distância, tipo de carga, modal e transportadora ao preço. Com essa regra, o modelo calcula um preço esperado para cada cotação e compara com o que foi cobrado.

Passo a passo:

Separação dos dados: 75% das cotações são usadas para o modelo aprender (treino) e 25% ficam guardadas para testar se ele acerta em casos que nunca viu (teste).
Preparação: peso e distância são colocados na mesma escala, e as categorias (como "Aéreo" ou "Frágil") são transformadas em colunas de 0 e 1 que o modelo consegue usar (one-hot encoding).
Treino: o modelo LinearRegression do scikit-learn aprende a relação entre as variáveis e o preço.
Avaliação: calcula MAE, RMSE e R² nos dados de teste (explicados em Métricas).
Limite de alerta: o modelo mede o tamanho típico dos seus próprios erros no treino e define a partir disso o quanto uma diferença pode ser considerada "normal" (detalhes em Regra de alerta).
Classificação: cada cotação recebe o status REVISAR ou DENTRO DO PADRAO, exportado em CSV.
Regra de alerta

Uma cotação recebe REVISAR quando qualquer uma das condições abaixo acontece:

A diferença em reais é grande demais: fica acima do limite de alerta, que é 3 vezes o erro típico do modelo, com mínimo de R$ 100.
A diferença em percentual é grande demais: passa de 25% do preço esperado e também passa de R$ 100 (para não alertar por diferenças pequenas em fretes baratos).

Como o erro típico é medido: usa-se o desvio absoluto mediano (MAD) dos erros de treino, ajustado para ficar na mesma escala de um desvio padrão. Diferente da média, a mediana não é puxada por poucos valores extremos, então o limite não fica inflado pelas próprias cotações problemáticas.

Como executar

Pré-requisito: Python 3.10 ou superior.

bash
pip install -r requirements.txt
python src/simulador_frete.py

As tabelas de resultado são salvas em outputs/ e os gráficos em images/.

Estrutura do projeto
simulador_precificacao_frete/
├── dados/
│   └── historico_cotacoes_ficticio.csv   # 240 cotações fictícias
├── images/
│   ├── real_vs_estimado.png              # preço cobrado x preço esperado
│   └── residuos_alertas.png              # diferenças e cotações em alerta
├── outputs/
│   ├── avaliacao_cotacoes_exemplo.csv    # status de cada cotação
│   └── simulacao_nova_cotacao.csv        # exemplo de estimativa para uma nova cotação
├── src/
│   └── simulador_frete.py                # script principal
├── requirements.txt
└── README.md
Resultados

Show Image

Show Image

<!-- Sugestão: adicione aqui os valores de MAE, RMSE e R² obtidos, por exemplo: | Métrica | Valor | |---|---| | MAE | R$ ... | | RMSE | R$ ... | | R² | ... | -->
Como interpretar a saída
Coluna / status	Significado
preco_esperado_brl	Preço calculado pelo modelo
diferenca_brl	Preço cobrado menos preço esperado. Positivo = cobrado acima do esperado; negativo = abaixo
diferenca_pct	A mesma diferença, em % do preço esperado
REVISAR	A cotação atingiu pelo menos uma condição da regra de alerta
DENTRO DO PADRAO	Nenhuma condição de alerta foi atingida

Um alerta é um indício para revisão, não uma prova de erro. O preço real pode variar por pedágios, combustível, urgência, rota real, seguro, sazonalidade, capacidade disponível, impostos e condições comerciais que não estão no histórico.

Métricas
MAE (erro absoluto médio): em média, quantos reais o modelo erra para mais ou para menos. Quanto menor, melhor.
RMSE (raiz do erro quadrático médio): também em reais, mas pesa mais os erros grandes. Se o RMSE for bem maior que o MAE, há alguns erros grandes puxando o resultado.
R²: de 0 a 1, indica quanto da variação dos preços o modelo consegue explicar. Por exemplo, 0,85 significa que ele explica 85% dessa variação.

Todas são calculadas nos dados de teste, ou seja, em cotações que o modelo não usou para aprender.

Limitações
Os dados são artificiais, criados para fins educacionais.
A regressão linear é um modelo de referência simples: assume que cada fator soma um efeito fixo ao preço e pode não captar relações mais complexas (por exemplo, o preço por km cair em distâncias longas).
O histórico não inclui todas as variáveis comerciais relevantes.
Para uso real, seria preciso validar o modelo com cotações de períodos posteriores, revisar os limites de alerta e evitar estimar preços para combinações muito diferentes das que aparecem no histórico.

Antonio Aguiar
