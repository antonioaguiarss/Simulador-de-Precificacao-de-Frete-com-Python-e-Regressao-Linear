"""
Simulador simples de precificação de frete com regressão linear.
Todos os dados são fictícios.
Uso: pip install -r requirements.txt && python src/simulador_frete.py
"""
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "dados" / "historico_cotacoes_ficticio.csv"
OUT = ROOT / "outputs"
IMG = ROOT / "images"
OUT.mkdir(exist_ok=True)
IMG.mkdir(exist_ok=True)

NUM_COLS = ["peso_kg", "distancia_km"]
CAT_COLS = ["tipo_carga", "modal", "transportadora"]
FEATURES = NUM_COLS + CAT_COLS
TARGET = "preco_cobrado_brl"

def criar_modelo():
    """Regressão linear com variáveis categóricas codificadas (one-hot)."""
    preprocessor = ColumnTransformer([
        ("numericas", StandardScaler(), NUM_COLS),
        ("categoricas", OneHotEncoder(handle_unknown="ignore"), CAT_COLS),
    ])
    return Pipeline([
        ("preprocessador", preprocessor),
        ("regressao_linear", LinearRegression()),
    ])

def limite_robusto_alerta(residuos, piso=100.0):
    """Limite baseado no MAD, menos sensível a resíduos extremos que o desvio padrão."""
    residuos = np.asarray(residuos)
    mediana = np.median(residuos)
    mad = np.median(np.abs(residuos - mediana))
    return max(3 * 1.4826 * mad, piso)

def avaliar_cotacoes(df, modelo, limite_alerta):
    resultado = df.copy()
    resultado["preco_esperado_brl"] = modelo.predict(resultado[FEATURES]).round(2)
    resultado["diferenca_brl"] = (resultado[TARGET] - resultado["preco_esperado_brl"]).round(2)
    resultado["diferenca_pct"] = (resultado["diferenca_brl"] / resultado["preco_esperado_brl"] * 100).round(2)
    alerta_absoluto = resultado["diferenca_brl"].abs() > limite_alerta
    alerta_percentual = (
        (resultado["diferenca_pct"].abs() > 25) &
        (resultado["diferenca_brl"].abs() > 100)
    )
    resultado["status"] = np.where(
        alerta_absoluto | alerta_percentual, "REVISAR", "DENTRO DO PADRAO"
    )
    resultado["limite_alerta_brl"] = round(float(limite_alerta), 2)
    return resultado

def simular_nova_cotacao(modelo, limite_alerta, cotacao, preco_cotado):
    entrada = pd.DataFrame([cotacao])
    esperado = float(modelo.predict(entrada[FEATURES])[0])
    diferenca = float(preco_cotado) - esperado
    return {
        **cotacao,
        "preco_cotado_brl": round(float(preco_cotado), 2),
        "preco_esperado_brl": round(esperado, 2),
        "diferenca_brl": round(diferenca, 2),
        "diferenca_pct": round(diferenca / esperado * 100, 2),
        "status": "REVISAR" if (
            abs(diferenca) > limite_alerta or
            (abs(diferenca / esperado * 100) > 25 and abs(diferenca) > 100)
        ) else "DENTRO DO PADRAO",
        "limite_alerta_brl": round(float(limite_alerta), 2),
    }

def main():
    df = pd.read_csv(DATA)
    df[TARGET] = pd.to_numeric(df[TARGET], errors="coerce")
    df = df.dropna(subset=FEATURES + [TARGET])
    X, y = df[FEATURES], df[TARGET]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

    modelo = criar_modelo()
    modelo.fit(X_train, y_train)
    pred_test = modelo.predict(X_test)
    print("Avaliação no conjunto de teste:")
    print(f"MAE: R$ {mean_absolute_error(y_test, pred_test):,.2f}")
    print(f"RMSE: R$ {mean_squared_error(y_test, pred_test) ** 0.5:,.2f}")
    print(f"R²: {r2_score(y_test, pred_test):.3f}")

    residuos_treino = y_train.to_numpy() - modelo.predict(X_train)
    limite_alerta = limite_robusto_alerta(residuos_treino)

    # Para demonstrar o relatório histórico, reajusta com todo o histórico.
    # Em produção, a avaliação do desempenho deve ser feita em dados futuros.
    modelo.fit(X, y)
    avaliadas = avaliar_cotacoes(df, modelo, limite_alerta)
    avaliadas.to_csv(OUT / "avaliacao_cotacoes_exemplo.csv", index=False)

    nova = {"peso_kg": 2500, "distancia_km": 1200, "tipo_carga": "Geral",
            "modal": "Rodoviário", "transportadora": "TransLog"}
    preco_cotado = float(modelo.predict(pd.DataFrame([nova]))[0] * 1.32)
    simulacao = simular_nova_cotacao(modelo, limite_alerta, nova, preco_cotado)
    pd.DataFrame([simulacao]).to_csv(OUT / "simulacao_nova_cotacao.csv", index=False)
    print("\\nExemplo de nova cotação:")
    print(pd.Series(simulacao).to_string())

    # Gráfico real x estimado no conjunto de teste
    plt.figure(figsize=(8, 6))
    plt.scatter(y_test, pred_test, alpha=0.75)
    limites = [min(y_test.min(), pred_test.min()), max(y_test.max(), pred_test.max())]
    plt.plot(limites, limites, linestyle="--")
    plt.xlabel("Preço real (R$)"); plt.ylabel("Preço estimado (R$)")
    plt.title("Regressão linear: preço real x estimado")
    plt.tight_layout(); plt.savefig(IMG / "real_vs_estimado.png", dpi=160); plt.close()

    residuos = y_test.to_numpy() - pred_test
    plt.figure(figsize=(9, 5))
    plt.hist(residuos, bins=24, edgecolor="black")
    plt.axvline(limite_alerta, linestyle="--", label=f"Limite +R$ {limite_alerta:.0f}")
    plt.axvline(-limite_alerta, linestyle="--", label=f"Limite -R$ {limite_alerta:.0f}")
    plt.xlabel("Resíduo (preço real - estimado), R$"); plt.ylabel("Quantidade de cotações")
    plt.title("Distribuição dos resíduos"); plt.legend()
    plt.tight_layout(); plt.savefig(IMG / "residuos_alertas.png", dpi=160); plt.close()
    print("\\nArquivos gerados em outputs/ e images/.")

if __name__ == "__main__":
    main()
