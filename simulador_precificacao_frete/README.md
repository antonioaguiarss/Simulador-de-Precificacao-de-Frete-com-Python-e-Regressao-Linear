# Simulador de Precificação de Frete com Regressão Linear

Projeto de portfólio com histórico **100% fictício** de 240 cotações de frete. Estima um preço esperado a partir de peso, distância, tipo de carga, modal e transportadora, e sinaliza cotações cujo preço real se afasta muito do esperado.

## Objetivos
- Aplicar regressão linear básica com variáveis numéricas e categóricas.
- Comparar preço real com preço estimado.
- Sinalizar valores que merecem revisão, sem afirmar automaticamente que estão errados.
- Gerar indicadores simples de avaliação do modelo.

## Variáveis
- `peso_kg`: peso da carga em kg.
- `distancia_km`: distância estimada em km.
- `tipo_carga`: Geral, Refrigerada, Perigosa ou Frágil.
- `modal`: Rodoviário, Aéreo ou Marítimo.
- `transportadora`: transportadora fictícia.
- `preco_cobrado_brl`: preço cobrado em reais.

## Como funciona
1. Divide os dados em treino e teste (75%/25%).
2. Padroniza as variáveis numéricas e transforma as categorias em variáveis indicadoras (one-hot encoding).
3. Treina uma `LinearRegression` do scikit-learn.
4. Calcula MAE, RMSE e R² no conjunto de teste.
5. Define um limite robusto de alerta com base em três vezes o desvio absoluto mediano (MAD) dos resíduos de treino, convertido para uma escala comparável ao desvio padrão (piso de R$ 100).
6. Compara cotações com o preço esperado e exporta o status `REVISAR` ou `DENTRO DO PADRAO`. O alerta ocorre se a diferença absoluta superar o limite robusto ou se a diferença percentual exceder 25% com diferença absoluta acima de R$ 100.

## Executar
Requer Python 3.10+.

```bash
pip install -r requirements.txt
python src/simulador_frete.py
```

Os resultados ficam em `outputs/` e os gráficos em `images/`.

## Arquivos
```text
simulador_precificacao_frete/
├── dados/
│   └── historico_cotacoes_ficticio.csv
├── images/
│   ├── real_vs_estimado.png
│   └── residuos_alertas.png
├── outputs/
│   ├── avaliacao_cotacoes_exemplo.csv
│   └── simulacao_nova_cotacao.csv
├── src/
│   └── simulador_frete.py
├── requirements.txt
└── README.md
```

## Como interpretar
- `preco_esperado_brl`: previsão da regressão.
- `diferenca_brl`: preço cobrado menos preço esperado. Positivo significa acima do esperado; negativo, abaixo.
- `diferenca_pct`: diferença percentual em relação ao esperado.
- `REVISAR`: diferença absoluta maior que o limite de alerta.
- `DENTRO DO PADRAO`: não ultrapassou o limite definido.

Um alerta é apenas um indício para revisão. O preço pode variar por pedágios, combustível, urgência, rota real, seguro, sazonalidade, capacidade disponível, impostos e condições comerciais não representadas no histórico.

## Métricas
- **MAE:** erro absoluto médio das previsões.
- **RMSE:** penaliza mais os erros maiores.
- **R²:** proporção da variação explicada pelo modelo, calculada no conjunto de teste.

## Limitações
- Dados artificiais, criados para fins educacionais.
- Regressão linear é um modelo de referência simples; não captura necessariamente relações não lineares.
- O histórico não inclui todas as variáveis comerciais relevantes.
- Para uso real, validar em períodos futuros, revisar limites de alerta e evitar usar previsões sobre combinações muito diferentes das observadas no treino.

## Tecnologias
Python, pandas, NumPy, Matplotlib e scikit-learn.

## Sugestão de narrativa para entrevista
“Desenvolvi um simulador de precificação com regressão linear para estimar o preço esperado de frete a partir das características da carga e da operação. Comparei a previsão com o valor cotado, medi o erro no conjunto de teste e criei alertas para priorizar cotações fora do padrão. A ideia não é rejeitar automaticamente uma tarifa, mas direcionar a análise para casos que merecem validação.”

---
**Aviso:** todas as cotações são fictícias e não representam preços de mercado.
