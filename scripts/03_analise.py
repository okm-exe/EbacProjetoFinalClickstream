# ============================================================
# 03_analise.py
# Projeto Final - Analista de Dados
#
# Objetivo:
# Realizar análises sobre as bases tratadas e gerar tabelas
# agregadas para utilização posterior nas visualizações e
# no dashboard do projeto.
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================
# 1. CONFIGURAÇÃO DOS CAMINHOS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PROCESSED = BASE_DIR / "data" / "processed"

# Pasta onde serão salvas as tabelas geradas pelas análises
DATA_ANALYSIS = DATA_PROCESSED / "analysis"

DATA_ANALYSIS.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. CARREGAMENTO DAS BASES TRATADAS
# ============================================================

print("=" * 60)
print("CARREGANDO BASES TRATADAS")
print("=" * 60)

customers = pd.read_csv(DATA_PROCESSED / "customers_processed.csv")
products = pd.read_csv(DATA_PROCESSED / "products_processed.csv")
sessions = pd.read_csv(DATA_PROCESSED / "sessions_processed.csv")
events = pd.read_csv(DATA_PROCESSED / "events_processed.csv")
orders = pd.read_csv(DATA_PROCESSED / "orders_processed.csv")
order_items = pd.read_csv(DATA_PROCESSED / "order_items_processed.csv")
reviews = pd.read_csv(DATA_PROCESSED / "reviews_processed.csv")


# Conversão das datas necessárias para as análises
sessions["start_time"] = pd.to_datetime(sessions["start_time"])
events["timestamp"] = pd.to_datetime(events["timestamp"])
orders["order_time"] = pd.to_datetime(orders["order_time"])
reviews["review_time"] = pd.to_datetime(reviews["review_time"])


print(f"customers: {customers.shape}")
print(f"products: {products.shape}")
print(f"sessions: {sessions.shape}")
print(f"events: {events.shape}")
print(f"orders: {orders.shape}")
print(f"order_items: {order_items.shape}")
print(f"reviews: {reviews.shape}")


# ============================================================
# 3. ANÁLISE DO FUNIL DE CONVERSÃO
# ============================================================

print("\n" + "=" * 60)
print("ANÁLISE 1 - FUNIL DE CONVERSÃO")
print("=" * 60)

# Cada sessão pode possuir vários eventos.
# Por isso contamos session_id únicos em cada etapa.

etapas_funil = [
    "page_view",
    "add_to_cart",
    "checkout",
    "purchase"
]

funil = []

for etapa in etapas_funil:

    sessoes = events.loc[
        events["event_type"] == etapa,
        "session_id"
    ].nunique()

    funil.append({
        "etapa": etapa,
        "sessoes": sessoes
    })

funil = pd.DataFrame(funil)

# Percentual em relação ao total de sessões
total_sessoes = sessions["session_id"].nunique()

funil["taxa_percentual"] = (
    funil["sessoes"] / total_sessoes * 100
).round(2)

# Taxa de passagem entre uma etapa e a seguinte
funil["taxa_passagem_percentual"] = None

for i in range(1, len(funil)):

    atual = funil.loc[i, "sessoes"]
    anterior = funil.loc[i - 1, "sessoes"]

    funil.loc[i, "taxa_passagem_percentual"] = round(
        atual / anterior * 100,
        2
    )

print(funil)

funil.to_csv(
    DATA_ANALYSIS / "analise_funil.csv",
    index=False
)


# Gráfico do funil
plt.figure(figsize=(10, 6))

plt.bar(
    funil["etapa"],
    funil["sessoes"]
)

plt.title("Funil de conversão por etapa")
plt.xlabel("Etapa")
plt.ylabel("Número de sessões")

plt.tight_layout()

plt.savefig(
    DATA_ANALYSIS / "grafico_funil.png",
    dpi=300
)

plt.show()


# ============================================================
# 4. ANÁLISE DE CONVERSÃO POR FONTE DE TRÁFEGO
# ============================================================

print("\n" + "=" * 60)
print("ANÁLISE 2 - CONVERSÃO POR FONTE")
print("=" * 60)

# Relacionamos sessões com eventos para descobrir quantas
# sessões de cada fonte chegaram até uma compra.

sessoes_com_compra = (
    events.loc[
        events["event_type"] == "purchase",
        "session_id"
    ]
    .drop_duplicates()
)

analise_canais = (
    sessions
    .groupby("source")
    .agg(
        sessoes=("session_id", "nunique")
    )
    .reset_index()
)

compras_por_canal = (
    sessions[
        sessions["session_id"].isin(sessoes_com_compra)
    ]
    .groupby("source")
    .agg(
        sessoes_com_compra=("session_id", "nunique")
    )
    .reset_index()
)

analise_canais = analise_canais.merge(
    compras_por_canal,
    on="source",
    how="left"
)

analise_canais["sessoes_com_compra"] = (
    analise_canais["sessoes_com_compra"]
    .fillna(0)
    .astype(int)
)

analise_canais["taxa_conversao_percentual"] = (
    analise_canais["sessoes_com_compra"]
    / analise_canais["sessoes"]
    * 100
).round(2)

analise_canais = analise_canais.sort_values(
    "taxa_conversao_percentual",
    ascending=False
)

print(analise_canais)

analise_canais.to_csv(
    DATA_ANALYSIS / "analise_canais.csv",
    index=False
)


# Gráfico
plt.figure(figsize=(10, 6))

plt.bar(
    analise_canais["source"],
    analise_canais["taxa_conversao_percentual"]
)

plt.title("Taxa de conversão por fonte de tráfego")
plt.xlabel("Fonte")
plt.ylabel("Taxa de conversão (%)")

plt.tight_layout()

plt.savefig(
    DATA_ANALYSIS / "grafico_conversao_canais.png",
    dpi=300
)

plt.show()


# ============================================================
# 5. ANÁLISE DE VENDAS POR CATEGORIA
# ============================================================

print("\n" + "=" * 60)
print("ANÁLISE 3 - VENDAS POR CATEGORIA")
print("=" * 60)

# Relacionamos os itens vendidos aos produtos para obter
# a categoria de cada produto.

itens_com_categoria = order_items.merge(
    products[
        [
            "product_id",
            "category",
            "price_usd",
            "cost_usd",
            "margin_usd",
            "margin_pct"
        ]
    ],
    on="product_id",
    how="left"
)

analise_categorias = (
    itens_com_categoria
    .groupby("category")
    .agg(
        unidades_vendidas=("quantity", "sum"),
        receita_usd=("line_total_usd", "sum"),
        produtos_diferentes=("product_id", "nunique")
    )
    .reset_index()
)

analise_categorias["receita_media_por_unidade"] = (
    analise_categorias["receita_usd"]
    / analise_categorias["unidades_vendidas"]
).round(2)

analise_categorias["receita_usd"] = (
    analise_categorias["receita_usd"]
    .round(2)
)

analise_categorias = analise_categorias.sort_values(
    "receita_usd",
    ascending=False
)

print(analise_categorias)

analise_categorias.to_csv(
    DATA_ANALYSIS / "analise_categorias.csv",
    index=False
)


# Gráfico de receita
plt.figure(figsize=(10, 6))

plt.bar(
    analise_categorias["category"],
    analise_categorias["receita_usd"]
)

plt.title("Receita total por categoria")
plt.xlabel("Categoria")
plt.ylabel("Receita (US$)")

plt.xticks(rotation=30)

plt.tight_layout()

plt.savefig(
    DATA_ANALYSIS / "grafico_receita_categoria.png",
    dpi=300
)

plt.show()


# ============================================================
# 6. ANÁLISE DE PREÇO E MARGEM POR CATEGORIA
# ============================================================

print("\n" + "=" * 60)
print("ANÁLISE 4 - PREÇO E MARGEM POR CATEGORIA")
print("=" * 60)

preco_margem_categoria = (
    products
    .groupby("category")
    .agg(
        preco_medio_usd=("price_usd", "mean"),
        preco_mediano_usd=("price_usd", "median"),
        margem_media_usd=("margin_usd", "mean"),
        margem_mediana_usd=("margin_usd", "median"),
        margem_percentual_media=("margin_pct", "mean")
    )
    .reset_index()
)

colunas_numericas = [
    "preco_medio_usd",
    "preco_mediano_usd",
    "margem_media_usd",
    "margem_mediana_usd",
    "margem_percentual_media"
]

preco_margem_categoria[colunas_numericas] = (
    preco_margem_categoria[colunas_numericas]
    .round(2)
)

print(preco_margem_categoria)

preco_margem_categoria.to_csv(
    DATA_ANALYSIS / "analise_preco_margem.csv",
    index=False
)


# Gráfico da margem mediana
preco_margem_grafico = preco_margem_categoria.sort_values(
    "margem_mediana_usd"
)

plt.figure(figsize=(10, 6))

plt.barh(
    preco_margem_grafico["category"],
    preco_margem_grafico["margem_mediana_usd"]
)

plt.title("Margem mediana por categoria")
plt.xlabel("Margem mediana (US$)")
plt.ylabel("Categoria")

plt.tight_layout()

plt.savefig(
    DATA_ANALYSIS / "grafico_margem_categoria.png",
    dpi=300
)

plt.show()


# ============================================================
# 7. EVOLUÇÃO MENSAL DE PEDIDOS E RECEITA
# ============================================================

print("\n" + "=" * 60)
print("ANÁLISE 5 - EVOLUÇÃO MENSAL")
print("=" * 60)

pedidos_mensais = (
    orders
    .groupby("order_month")
    .agg(
        pedidos=("order_id", "nunique"),
        receita_usd=("total_usd", "sum")
    )
    .reset_index()
)

pedidos_mensais["receita_usd"] = (
    pedidos_mensais["receita_usd"]
    .round(2)
)

print(pedidos_mensais)

pedidos_mensais.to_csv(
    DATA_ANALYSIS / "analise_mensal.csv",
    index=False
)


# Gráfico de pedidos por mês
plt.figure(figsize=(14, 6))

plt.plot(
    pedidos_mensais["order_month"],
    pedidos_mensais["pedidos"],
    marker="o",
    markersize=3
)

plt.title("Evolução mensal do número de pedidos")
plt.xlabel("Mês")
plt.ylabel("Número de pedidos")

# Mostra apenas parte dos rótulos para evitar poluição visual
intervalo = max(1, len(pedidos_mensais) // 12)

plt.xticks(
    range(0, len(pedidos_mensais), intervalo),
    pedidos_mensais["order_month"].iloc[::intervalo],
    rotation=45
)

plt.tight_layout()

plt.savefig(
    DATA_ANALYSIS / "grafico_pedidos_mensais.png",
    dpi=300
)

plt.show()


# Gráfico de receita por mês
plt.figure(figsize=(14, 6))

plt.plot(
    pedidos_mensais["order_month"],
    pedidos_mensais["receita_usd"],
    marker="o",
    markersize=3
)

plt.title("Evolução mensal da receita")
plt.xlabel("Mês")
plt.ylabel("Receita (US$)")

plt.xticks(
    range(0, len(pedidos_mensais), intervalo),
    pedidos_mensais["order_month"].iloc[::intervalo],
    rotation=45
)

plt.tight_layout()

plt.savefig(
    DATA_ANALYSIS / "grafico_receita_mensal.png",
    dpi=300
)

plt.show()


# ============================================================
# 8. ANÁLISE DE AVALIAÇÕES POR CATEGORIA
# ============================================================

print("\n" + "=" * 60)
print("ANÁLISE 6 - AVALIAÇÕES POR CATEGORIA")
print("=" * 60)

reviews_categoria = reviews.merge(
    products[
        [
            "product_id",
            "category"
        ]
    ],
    on="product_id",
    how="left"
)

analise_reviews = (
    reviews_categoria
    .groupby("category")
    .agg(
        quantidade_avaliacoes=("review_id", "count"),
        avaliacao_media=("rating", "mean"),
        avaliacao_mediana=("rating", "median")
    )
    .reset_index()
)

analise_reviews[
    [
        "avaliacao_media",
        "avaliacao_mediana"
    ]
] = (
    analise_reviews[
        [
            "avaliacao_media",
            "avaliacao_mediana"
        ]
    ].round(2)
)

analise_reviews = analise_reviews.sort_values(
    "avaliacao_media",
    ascending=False
)

print(analise_reviews)

analise_reviews.to_csv(
    DATA_ANALYSIS / "analise_reviews_categoria.csv",
    index=False
)


# Gráfico
plt.figure(figsize=(10, 6))

plt.bar(
    analise_reviews["category"],
    analise_reviews["avaliacao_media"]
)

plt.title("Avaliação média por categoria")
plt.xlabel("Categoria")
plt.ylabel("Avaliação média")

plt.ylim(0, 5)

plt.xticks(rotation=30)

plt.tight_layout()

plt.savefig(
    DATA_ANALYSIS / "grafico_avaliacao_categoria.png",
    dpi=300
)

plt.show()


# ============================================================
# 9. RESUMO FINAL
# ============================================================

print("\n" + "=" * 60)
print("ANÁLISES CONCLUÍDAS")
print("=" * 60)

print("\nArquivos gerados:")

arquivos = [
    "analise_funil.csv",
    "analise_canais.csv",
    "analise_categorias.csv",
    "analise_preco_margem.csv",
    "analise_mensal.csv",
    "analise_reviews_categoria.csv"
]

for arquivo in arquivos:
    print(f"- {DATA_ANALYSIS / arquivo}")

print("\nGráficos também foram salvos na pasta:")
print(DATA_ANALYSIS)

print("\nProcesso de análise concluído com sucesso.")