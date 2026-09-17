import pandas as pd
from pathlib import Path


# ============================================================
# 1. CONFIGURAÇÃO DOS CAMINHOS
# ============================================================
# Os arquivos da pasta "raw" são os dados originais e não serão
# alterados. Os dados tratados serão salvos em "processed".

BASE_DIR = Path("ProjetoFinal")
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. CARREGAMENTO DAS BASES
# ============================================================

arquivos = {
    "customers": RAW_DIR / "customers.csv",
    "products": RAW_DIR / "products.csv",
    "sessions": RAW_DIR / "sessions.csv",
    "events": RAW_DIR / "events.csv",
    "orders": RAW_DIR / "orders.csv",
    "order_items": RAW_DIR / "order_items.csv",
    "reviews": RAW_DIR / "reviews.csv"
}

dfs = {}

for nome, caminho in arquivos.items():
    dfs[nome] = pd.read_csv(caminho)
    print(f"{nome}: {dfs[nome].shape}")


# ============================================================
# 3. PADRONIZAÇÃO DOS NOMES E TEXTOS
# ============================================================
# Padronizamos os nomes das colunas e removemos espaços extras
# dos campos de texto.

for nome, df in dfs.items():

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
    )

    # Pandas 3/4: usamos include="str" para selecionar strings.
    colunas_texto = df.select_dtypes(include="str").columns

    for coluna in colunas_texto:
        df[coluna] = df[coluna].str.strip()


# Padronização de categorias e campos de controle.

dfs["events"]["event_type"] = (
    dfs["events"]["event_type"].str.lower()
)

dfs["sessions"]["device"] = (
    dfs["sessions"]["device"].str.lower()
)

dfs["sessions"]["source"] = (
    dfs["sessions"]["source"].str.lower()
)

dfs["orders"]["payment_method"] = (
    dfs["orders"]["payment_method"].str.lower()
)

dfs["events"]["payment"] = (
    dfs["events"]["payment"].str.lower()
)


# ============================================================
# 4. CONVERSÃO DOS TIPOS DE DATA
# ============================================================
# As datas estavam armazenadas como strings na base original.
# Aqui fazemos a conversão definitiva para datetime.

colunas_data = {
    "customers": ["signup_date"],
    "sessions": ["start_time"],
    "events": ["timestamp"],
    "orders": ["order_time"],
    "reviews": ["review_time"]
}

for tabela, colunas in colunas_data.items():
    for coluna in colunas:
        dfs[tabela][coluna] = pd.to_datetime(
            dfs[tabela][coluna],
            errors="coerce"
        )


# Verificação de datas inválidas.

for tabela, colunas in colunas_data.items():
    for coluna in colunas:

        invalidas = dfs[tabela][coluna].isna().sum()

        if invalidas > 0:
            raise ValueError(
                f"{tabela}.{coluna}: {invalidas} datas inválidas "
                "foram encontradas após a conversão."
            )


# ============================================================
# 5. PADRONIZAÇÃO DOS TIPOS NUMÉRICOS
# ============================================================

colunas_numericas = {
    "customers": ["age"],
    "products": ["price_usd", "cost_usd", "margin_usd"],
    "events": ["qty", "cart_size", "discount_pct", "amount_usd"],
    "orders": ["discount_pct", "subtotal_usd", "total_usd"],
    "order_items": [
        "unit_price_usd",
        "quantity",
        "line_total_usd"
    ],
    "reviews": ["rating"]
}

for tabela, colunas in colunas_numericas.items():
    for coluna in colunas:
        dfs[tabela][coluna] = pd.to_numeric(
            dfs[tabela][coluna],
            errors="coerce"
        )


# ============================================================
# 6. TRATAMENTO DE DUPLICIDADES
# ============================================================
# Removemos somente linhas totalmente duplicadas.
#
# Na exploração foram encontradas 73 linhas duplicadas em
# order_items. Como os registros são exatamente iguais, manter
# as cópias duplicaria artificialmente unidades e receita.
#
# Não removemos registros apenas por possuírem o mesmo order_id
# ou product_id, pois um pedido pode possuir diferentes produtos.

for nome, df in dfs.items():

    antes = len(df)

    dfs[nome] = df.drop_duplicates().copy()

    removidas = antes - len(dfs[nome])

    print(
        f"{nome}: {removidas} linhas duplicadas removidas."
    )


# ============================================================
# 7. TRATAMENTO DOS VALORES AUSENTES
# ============================================================
# A exploração mostrou que os valores ausentes de "events" são
# estruturais e dependem do tipo de evento.
#
# Exemplo:
# - page_view não precisa de pagamento ou valor da compra;
# - add_to_cart não possui dados de pagamento;
# - checkout não possui necessariamente produto/quantidade;
# - purchase possui os dados relacionados à compra.
#
# Portanto, NÃO preenchemos esses valores com zero e NÃO removemos
# essas linhas. Preencher ou excluir esses campos alteraria o
# significado original dos eventos.
#
# O tratamento realizado aqui é a validação de que os nulos estão
# de acordo com o padrão observado por tipo de evento.

print("\n" + "=" * 60)
print("VALORES AUSENTES - EVENTS")
print("=" * 60)

nulos_eventos = (
    dfs["events"]
    .groupby("event_type")
    .apply(lambda df: df.isna().sum())
)

print(nulos_eventos)


# Não esperamos nulos nas seguintes colunas fundamentais do evento.

colunas_obrigatorias_events = [
    "event_id",
    "session_id",
    "timestamp",
    "event_type"
]

for coluna in colunas_obrigatorias_events:

    nulos = dfs["events"][coluna].isna().sum()

    if nulos > 0:
        raise ValueError(
            f"events.{coluna} possui {nulos} valores ausentes."
        )


# Para as demais tabelas, verificamos se existem valores ausentes.
# Se houver, registramos a quantidade e interrompemos o processo,
# pois não temos uma regra segura para preenchê-los automaticamente.

for nome, df in dfs.items():

    if nome == "events":
        continue

    nulos_por_coluna = df.isna().sum()
    nulos = nulos_por_coluna.sum()

    print(f"\n{nome}: {nulos} valores ausentes.")

    if nulos > 0:
        print(nulos_por_coluna[nulos_por_coluna > 0])

        raise ValueError(
            f"A tabela {nome} possui valores ausentes. "
            "É necessário definir uma regra de tratamento."
        )


# ============================================================
# 8. VALIDAÇÕES DE CONSISTÊNCIA
# ============================================================
# Verificamos regras básicas de negócio e estrutura.
# Valores inválidos interrompem o processo para evitar salvar
# uma base inconsistente.

# Preços, custos e margens devem ser positivos.

if (dfs["products"]["price_usd"] <= 0).any():
    raise ValueError(
        "Existem produtos com preço menor ou igual a zero."
    )

if (dfs["products"]["cost_usd"] <= 0).any():
    raise ValueError(
        "Existem produtos com custo menor ou igual a zero."
    )

if (dfs["products"]["margin_usd"] <= 0).any():
    raise ValueError(
        "Existem produtos com margem menor ou igual a zero."
    )


# Quantidades vendidas devem ser positivas.

if (dfs["order_items"]["quantity"] <= 0).any():
    raise ValueError(
        "Existem itens de pedido com quantidade menor ou igual a zero."
    )


# Ratings devem estar entre 1 e 5.

if not dfs["reviews"]["rating"].between(1, 5).all():
    raise ValueError(
        "Existem avaliações fora da escala esperada de 1 a 5."
    )

print("\n" + "=" * 60)
print("ANÁLISE DOS DESCONTOS")
print("=" * 60)

for tabela in ["events", "orders"]:

    print(f"\n--- {tabela} ---")

    print("Mínimo:", dfs[tabela]["discount_pct"].min())
    print("Máximo:", dfs[tabela]["discount_pct"].max())

    print("\nValores abaixo de 0:")
    print(
        dfs[tabela][dfs[tabela]["discount_pct"] < 0]
        [["discount_pct"]]
        .value_counts()
    )

    print("\nValores acima de 100:")
    print(
        dfs[tabela][dfs[tabela]["discount_pct"] > 100]
        [["discount_pct"]]
        .value_counts()
    )
# Descontos devem estar entre 0% e 100%.

# Descontos existentes devem estar entre 0% e 100%.
# Valores nulos em events são esperados para eventos que não
# representam uma compra.

for tabela in ["events", "orders"]:

    descontos = dfs[tabela]["discount_pct"].dropna()

    if not descontos.between(0, 100).all():
        raise ValueError(
            f"Existem descontos inválidos na tabela {tabela}."
        )


# A margem cadastrada deve corresponder ao preço menos o custo.

margem_calculada = (
    dfs["products"]["price_usd"]
    - dfs["products"]["cost_usd"]
)

diferenca_margem = (
    dfs["products"]["margin_usd"]
    - margem_calculada
).abs()

if (diferenca_margem > 0.01).any():
    raise ValueError(
        "Existem produtos cuja margem não corresponde a "
        "price_usd - cost_usd."
    )


# O total do item deve corresponder ao preço unitário multiplicado
# pela quantidade, considerando pequena diferença de arredondamento.

total_calculado = (
    dfs["order_items"]["unit_price_usd"]
    * dfs["order_items"]["quantity"]
)

diferenca_total = (
    dfs["order_items"]["line_total_usd"]
    - total_calculado
).abs()

if (diferenca_total > 0.01).any():
    raise ValueError(
        "Existem itens cuja line_total_usd não corresponde "
        "a unit_price_usd * quantity."
    )


# ============================================================
# 9. COLUNAS DERIVADAS
# ============================================================
# Criamos novas variáveis a partir das existentes.
# Elas serão úteis para análises e para o dashboard.

# 1ª coluna derivada:
# margem percentual do produto.

dfs["products"]["margin_pct"] = (
    dfs["products"]["margin_usd"]
    / dfs["products"]["price_usd"]
    * 100
)


# 2ª coluna derivada:
# mês do pedido.

dfs["orders"]["order_month"] = (
    dfs["orders"]["order_time"]
    .dt.to_period("M")
    .astype(str)
)


# 3ª coluna derivada:
# ano do pedido.

dfs["orders"]["order_year"] = (
    dfs["orders"]["order_time"]
    .dt.year
)


# ============================================================
# 10. VALIDAÇÃO FINAL DOS IDENTIFICADORES
# ============================================================
# Confirmamos que os identificadores principais são únicos
# após o tratamento.

ids = {
    "customers": "customer_id",
    "products": "product_id",
    "sessions": "session_id",
    "events": "event_id",
    "orders": "order_id",
    "reviews": "review_id"
}

for tabela, coluna in ids.items():

    duplicados = dfs[tabela][coluna].duplicated().sum()

    if duplicados > 0:
        raise ValueError(
            f"{tabela}.{coluna} possui {duplicados} IDs duplicados."
        )


# ============================================================
# 11. VALIDAÇÃO DOS RELACIONAMENTOS
# ============================================================
# Confirmamos que as chaves estrangeiras possuem correspondência
# nas respectivas tabelas de referência.

relacionamentos = {
    "sessions -> customers": (
        "sessions", "customer_id",
        "customers", "customer_id"
    ),
    "events -> sessions": (
        "events", "session_id",
        "sessions", "session_id"
    ),
    "events -> products": (
        "events", "product_id",
        "products", "product_id"
    ),
    "orders -> customers": (
        "orders", "customer_id",
        "customers", "customer_id"
    ),
    "order_items -> orders": (
        "order_items", "order_id",
        "orders", "order_id"
    ),
    "order_items -> products": (
        "order_items", "product_id",
        "products", "product_id"
    ),
    "reviews -> orders": (
        "reviews", "order_id",
        "orders", "order_id"
    ),
    "reviews -> products": (
        "reviews", "product_id",
        "products", "product_id"
    )
}

for nome, (
    tabela_filha,
    coluna_filha,
    tabela_pai,
    coluna_pai
) in relacionamentos.items():

    valores_filha = set(
        dfs[tabela_filha][coluna_filha].dropna()
    )

    valores_pai = set(
        dfs[tabela_pai][coluna_pai].dropna()
    )

    faltantes = valores_filha - valores_pai

    if faltantes:
        raise ValueError(
            f"{nome}: {len(faltantes)} IDs sem correspondência."
        )


# ============================================================
# 12. VALIDAÇÃO FINAL
# ============================================================

print("\n" + "=" * 60)
print("VALIDAÇÃO FINAL")
print("=" * 60)

for nome, df in dfs.items():

    nulos = df.isna().sum().sum()

    print(
        f"{nome}: {len(df):,} linhas | "
        f"{len(df.columns)} colunas | "
        f"{nulos:,} valores ausentes"
    )

print("\nTratamento concluído sem erros.")


# ============================================================
# 13. SALVAMENTO DAS BASES TRATADAS
# ============================================================
# As bases tratadas são salvas em processed.
# Os arquivos originais em raw permanecem intactos.

for nome, df in dfs.items():

    caminho_saida = PROCESSED_DIR / f"{nome}_processed.csv"

    df.to_csv(
        caminho_saida,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"Salvo: {caminho_saida}")

print("\nTodas as bases tratadas foram salvas com sucesso.")
