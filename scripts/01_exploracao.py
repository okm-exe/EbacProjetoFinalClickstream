import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# 1. CARREGAMENTO DOS DADOS
# ============================================================
# As bases originais estão armazenadas na pasta data/raw.
# Mantemos os arquivos originais sem alterações e carregamos
# cada CSV em um DataFrame dentro do dicionário "dfs".

arquivos = {
    "customers": "ProjetoFinal/data/raw/customers.csv",
    "products": "ProjetoFinal/data/raw/products.csv",
    "sessions": "ProjetoFinal/data/raw/sessions.csv",
    "events": "ProjetoFinal/data/raw/events.csv",
    "orders": "ProjetoFinal/data/raw/orders.csv",
    "order_items": "ProjetoFinal/data/raw/order_items.csv",
    "reviews": "ProjetoFinal/data/raw/reviews.csv"
}

dfs = {}

for nome, caminho in arquivos.items():
    dfs[nome] = pd.read_csv(caminho)
    print(f"{nome}: {dfs[nome].shape}")


# ============================================================
# 2. ESTRUTURA DAS TABELAS
# ============================================================
# Verificamos o tamanho e as colunas de cada tabela.
# Essas informações ajudam a documentar a estrutura da base.

for nome, df in dfs.items():
    print(f"\n{'=' * 50}")
    print(f"TABELA: {nome}")
    print(f"{'=' * 50}")
    print(f"Linhas e colunas: {df.shape}")
    print("Colunas:")
    print(list(df.columns))


# ============================================================
# 3. VARIÁVEIS CATEGÓRICAS E EVENTOS
# ============================================================
# Verificamos os principais valores categóricos e os tipos de
# eventos do clickstream. Essas variáveis serão utilizadas em
# análises posteriores, principalmente no funil de conversão.

print("\n" + "=" * 50)
print("EVENTOS DO CLICKSTREAM")
print("=" * 50)
print(dfs["events"]["event_type"].value_counts())

print("\n" + "=" * 50)
print("DISPOSITIVOS")
print("=" * 50)
print(dfs["sessions"]["device"].value_counts())

print("\n" + "=" * 50)
print("FONTES DE TRÁFEGO")
print("=" * 50)
print(dfs["sessions"]["source"].value_counts())

print("\n" + "=" * 50)
print("MÉTODOS DE PAGAMENTO")
print("=" * 50)
print(dfs["orders"]["payment_method"].value_counts())


# ============================================================
# 4. VERIFICAÇÃO DAS DATAS
# ============================================================
# Identificamos as colunas relacionadas a datas e horários.
# Neste momento elas ainda estão armazenadas como texto (str).
# A conversão para datetime será feita na etapa de tratamento.

for nome, df in dfs.items():
    print(f"\n--- {nome} ---")

    for coluna in df.columns:
        if (
            "time" in coluna.lower()
            or "date" in coluna.lower()
            or "timestamp" in coluna.lower()
        ):
            print(f"{coluna} -> {df[coluna].dtype}")


# ============================================================
# 5. QUALIDADE DOS DADOS
# ============================================================
# Verificamos valores ausentes e linhas completamente duplicadas.
# Essas verificações fazem parte da avaliação inicial da qualidade
# dos dados antes da análise.

for nome, df in dfs.items():
    print(f"\n{'=' * 50}")
    print(f"QUALIDADE: {nome.upper()}")
    print(f"{'=' * 50}")

    print("\nValores nulos por coluna:")
    print(df.isna().sum())

    print(f"\nLinhas completamente duplicadas: {df.duplicated().sum()}")


# ============================================================
# 6. VALIDAÇÃO DOS RELACIONAMENTOS ENTRE AS TABELAS
# ============================================================
# Verificamos se os IDs utilizados para cruzar as tabelas possuem
# correspondência entre as tabelas dependentes e de referência.

relacionamentos = {
    "sessions -> customers": ("sessions", "customer_id", "customers", "customer_id"),
    "events -> sessions": ("events", "session_id", "sessions", "session_id"),
    "events -> products": ("events", "product_id", "products", "product_id"),
    "orders -> customers": ("orders", "customer_id", "customers", "customer_id"),
    "order_items -> orders": ("order_items", "order_id", "orders", "order_id"),
    "order_items -> products": ("order_items", "product_id", "products", "product_id"),
    "reviews -> orders": ("reviews", "order_id", "orders", "order_id"),
    "reviews -> products": ("reviews", "product_id", "products", "product_id")
}

for nome, (tabela_filha, coluna_filha, tabela_pai, coluna_pai) in relacionamentos.items():

    valores_filha = set(dfs[tabela_filha][coluna_filha].dropna())
    valores_pai = set(dfs[tabela_pai][coluna_pai].dropna())

    faltantes = valores_filha - valores_pai

    print(f"{nome}: {len(faltantes)} IDs sem correspondência")


# ============================================================
# 7. UNICIDADE DOS IDENTIFICADORES
# ============================================================
# Verificamos se os identificadores principais são únicos.
# Isso ajuda a confirmar a estrutura das tabelas e evita problemas
# em futuros cruzamentos.

ids = {
    "customers": "customer_id",
    "products": "product_id",
    "sessions": "session_id",
    "events": "event_id",
    "orders": "order_id",
    "reviews": "review_id"
}

for tabela, coluna in ids.items():
    total = len(dfs[tabela])
    unicos = dfs[tabela][coluna].nunique()
    duplicados = total - unicos

    print(f"{tabela}: {coluna} -> {unicos} únicos | {duplicados} duplicados")


# ============================================================
# 8. ANÁLISE EXPLORATÓRIA 1 - DISTRIBUIÇÃO DOS PREÇOS
# ============================================================
# O objetivo é entender a distribuição dos preços dos produtos
# e identificar valores potencialmente discrepantes.
#
# Utilizamos o intervalo interquartil (IQR) para identificar
# possíveis outliers. Um outlier estatístico não significa
# necessariamente um erro, portanto não removemos esses registros
# nesta etapa.

print("\n" + "=" * 50)
print("ANÁLISE 1 - DISTRIBUIÇÃO DOS PREÇOS")
print("=" * 50)

preco = dfs["products"]["price_usd"]

q1 = preco.quantile(0.25)
q3 = preco.quantile(0.75)
iqr = q3 - q1

limite_inferior = q1 - 1.5 * iqr
limite_superior = q3 + 1.5 * iqr

outliers = dfs["products"][
    (preco < limite_inferior) |
    (preco > limite_superior)
]

print(f"Q1: ${q1:.2f}")
print(f"Q3: ${q3:.2f}")
print(f"IQR: ${iqr:.2f}")
print(f"Limite inferior: ${limite_inferior:.2f}")
print(f"Limite superior: ${limite_superior:.2f}")
print(f"Quantidade de possíveis outliers: {len(outliers)}")

print("\nProdutos com maiores preços entre os possíveis outliers:")
print(
    outliers[["product_id", "category", "name", "price_usd"]]
    .sort_values("price_usd", ascending=False)
    .head(10)
)

# ============================================================
# 9. ANÁLISE EXPLORATÓRIA 2 - PREÇO E MARGEM POR CATEGORIA
# ============================================================
# Comparamos preço e margem entre as categorias de produtos.
# A mediana é apresentada junto à média para reduzir o efeito
# de valores extremos identificados na análise anterior.

analise_categoria = (
    dfs["products"]
    .groupby("category")
    .agg(
        preco_medio=("price_usd", "mean"),
        preco_mediano=("price_usd", "median"),
        margem_media=("margin_usd", "mean"),
        margem_mediana=("margin_usd", "median")
    )
    .sort_values("preco_mediano", ascending=False)
)

print("\n" + "=" * 50)
print("ANÁLISE 2 - PREÇO E MARGEM POR CATEGORIA")
print("=" * 50)
print(analise_categoria.round(2))

# Gráfico da margem mediana por categoria

plt.figure(figsize=(10, 5))

plt.barh(
    analise_categoria.index,
    analise_categoria["margem_mediana"]
)

plt.title("Margem mediana por categoria")
plt.xlabel("Margem mediana (USD)")
plt.ylabel("Categoria")

plt.tight_layout()
plt.show()

# ============================================================
# 10. ANÁLISE EXPLORATÓRIA 3 - FUNIL DE CONVERSÃO
# ============================================================
# Analisamos quantas sessões chegaram a cada etapa do processo
# de compra.
#
# Como uma mesma sessão pode possuir vários eventos do mesmo tipo,
# contamos session_id únicos para evitar que múltiplos eventos
# sejam interpretados como múltiplas sessões.

eventos_funil = ["page_view", "add_to_cart", "checkout", "purchase"]

sessoes_funil = (
    dfs["events"]
    .groupby("event_type")["session_id"]
    .nunique()
    .reindex(eventos_funil)
)

total_sessoes = dfs["sessions"]["session_id"].nunique()

print("\n" + "=" * 50)
print("ANÁLISE 3 - FUNIL DE CONVERSÃO")
print("=" * 50)

print(f"Total de sessões: {total_sessoes:,}")

for evento, quantidade in sessoes_funil.items():
    percentual = quantidade / total_sessoes * 100
    print(f"{evento}: {quantidade:,} sessões ({percentual:.2f}%)")


# Taxa de passagem entre cada etapa do funil

print("\nTaxas de passagem entre etapas:")

for i in range(1, len(eventos_funil)):
    etapa_anterior = sessoes_funil.iloc[i - 1]
    etapa_atual = sessoes_funil.iloc[i]

    taxa = etapa_atual / etapa_anterior * 100

    print(
        f"{eventos_funil[i - 1]} -> {eventos_funil[i]}: "
        f"{taxa:.2f}%"
    )


# Gráfico do funil

plt.figure(figsize=(10, 5))

plt.bar(
    eventos_funil,
    sessoes_funil.values
)

plt.title("Sessões por etapa do funil de conversão")
plt.xlabel("Etapa")
plt.ylabel("Sessões")

plt.tight_layout()
plt.show()

# ============================================================
# 11. ANÁLISE EXPLORATÓRIA 4 - CONVERSÃO POR FONTE DE TRÁFEGO
# ============================================================
# Comparamos as fontes de tráfego considerando a quantidade
# de sessões e a proporção de sessões que chegaram à compra.
#
# A conversão é calculada como:
#
# sessões com purchase / total de sessões da fonte * 100

sessions_com_fonte = dfs["sessions"][[
    "session_id",
    "source"
]].copy()

events_com_fonte = dfs["events"][[
    "session_id",
    "event_type"
]].merge(
    sessions_com_fonte,
    on="session_id",
    how="left"
)

total_por_fonte = (
    sessions_com_fonte
    .groupby("source")["session_id"]
    .nunique()
)

compras_por_fonte = (
    events_com_fonte[
        events_com_fonte["event_type"] == "purchase"
    ]
    .groupby("source")["session_id"]
    .nunique()
)

analise_fonte = pd.DataFrame({
    "sessoes": total_por_fonte,
    "sessoes_com_compra": compras_por_fonte
}).fillna(0)

analise_fonte["taxa_conversao"] = (
    analise_fonte["sessoes_com_compra"]
    / analise_fonte["sessoes"]
    * 100
)

analise_fonte = analise_fonte.sort_values(
    "taxa_conversao",
    ascending=False
)

print("\n" + "=" * 50)
print("ANÁLISE 4 - CONVERSÃO POR FONTE DE TRÁFEGO")
print("=" * 50)

print(analise_fonte.round(2))


# Gráfico da taxa de conversão por fonte

plt.figure(figsize=(10, 5))

plt.bar(
    analise_fonte.index,
    analise_fonte["taxa_conversao"]
)

plt.title("Taxa de conversão por fonte de tráfego")
plt.xlabel("Fonte de tráfego")
plt.ylabel("Taxa de conversão (%)")

plt.tight_layout()
plt.show()

# ============================================================
# 12. ANÁLISE EXPLORATÓRIA 5 - VENDAS POR CATEGORIA
# ============================================================
# Cruzamos os itens vendidos com a tabela de produtos para
# analisar a quantidade vendida e a receita gerada por categoria.
#
# line_total_usd representa o valor total de cada item dentro
# do pedido.

itens_com_produtos = dfs["order_items"].merge(
    dfs["products"][[
        "product_id",
        "category"
    ]],
    on="product_id",
    how="left"
)

vendas_categoria = (
    itens_com_produtos
    .groupby("category")
    .agg(
        unidades_vendidas=("quantity", "sum"),
        receita_usd=("line_total_usd", "sum")
    )
    .sort_values("receita_usd", ascending=False)
)

print("\n" + "=" * 50)
print("ANÁLISE 5 - VENDAS POR CATEGORIA")
print("=" * 50)

print(vendas_categoria.round(2))


# Gráfico da receita por categoria

plt.figure(figsize=(10, 5))

plt.barh(
    vendas_categoria.index,
    vendas_categoria["receita_usd"]
)

plt.title("Receita por categoria")
plt.xlabel("Receita (USD)")
plt.ylabel("Categoria")

plt.tight_layout()
plt.show()

# ============================================================
# 13. ANÁLISE EXPLORATÓRIA 6 - EVOLUÇÃO DAS VENDAS NO TEMPO
# ============================================================
# Analisamos a evolução da quantidade de pedidos e da receita
# ao longo do período disponível na base.
#
# A coluna order_time ainda está armazenada como texto. Por isso,
# fazemos uma conversão temporária para datetime nesta análise.
# A conversão definitiva será realizada no tratamento dos dados.

orders_temporal = dfs["orders"].copy()

orders_temporal["order_time"] = pd.to_datetime(
    orders_temporal["order_time"]
)

orders_temporal["mes"] = (
    orders_temporal["order_time"]
    .dt.to_period("M")
    .astype(str)
)

vendas_mensais = (
    orders_temporal
    .groupby("mes")
    .agg(
        pedidos=("order_id", "nunique"),
        receita_usd=("total_usd", "sum")
    )
)

print("\n" + "=" * 50)
print("ANÁLISE 6 - EVOLUÇÃO DAS VENDAS NO TEMPO")
print("=" * 50)

print(vendas_mensais.round(2))


# Gráfico da quantidade de pedidos por mês

plt.figure(figsize=(12, 5))

plt.plot(
    vendas_mensais.index,
    vendas_mensais["pedidos"],
    marker="o",
    markersize=3
)

plt.title("Evolução da quantidade de pedidos")
plt.xlabel("Mês")
plt.ylabel("Quantidade de pedidos")

# Exibe apenas um rótulo a cada 6 meses
plt.xticks(
    range(0, len(vendas_mensais), 6),
    vendas_mensais.index[::6],
    rotation=45
)

plt.tight_layout()
plt.show()


# Gráfico da receita por mês

plt.figure(figsize=(12, 5))

plt.plot(
    vendas_mensais.index,
    vendas_mensais["receita_usd"],
    marker="o",
    markersize=3
)

plt.title("Evolução da receita")
plt.xlabel("Mês")
plt.ylabel("Receita (USD)")

# Exibe apenas um rótulo a cada 6 meses
plt.xticks(
    range(0, len(vendas_mensais), 6),
    vendas_mensais.index[::6],
    rotation=45
)

plt.tight_layout()
plt.show()

# Boxplot para visualizar a distribuição dos preços e os valores
# identificados como possíveis outliers pelo método do IQR.

plt.figure(figsize=(10, 5))
plt.boxplot(preco)

plt.title("Distribuição dos preços dos produtos")
plt.ylabel("Preço (USD)")

plt.show()
