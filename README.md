# E-commerce Analytics

Projeto final desenvolvido durante o curso de **Analista de Dados da EBAC**.

O projeto utiliza dados de um e-commerce para analisar o comportamento dos usuários, o processo de compra, as vendas, as categorias de produtos, as fontes de tráfego e as avaliações dos clientes.

Os dados foram explorados, tratados e analisados utilizando Python e, posteriormente, apresentados em um dashboard interativo desenvolvido no Looker Studio.

## Acesso ao dashboard

[🔗 Acessar o dashboard no Looker Studio](https://datastudio.google.com/reporting/f043c2b9-b623-439e-9043-52cdf22da3e8)

## Dados utilizados

[🔗 Acessar o dataset no Kaggle](https://www.kaggle.com/datasets/wafaaelhusseini/e-commerce-transactions-clickstream)

Os arquivos `events.csv` e `events_processed.csv` do projeto não foram incluídos no repositório devido ao limite de tamanho de 25mb do GitHub.


---

## Objetivo

O objetivo do projeto é transformar os dados disponíveis em informações que permitam compreender melhor o desempenho do e-commerce.

Entre os principais pontos analisados estão:

- comportamento dos usuários durante a jornada de compra;
- conversão das sessões em pedidos;
- desempenho das fontes de tráfego;
- vendas e receita por categoria;
- preço e margem dos produtos;
- evolução mensal dos pedidos e da receita;
- avaliações dos produtos.

---

As bases utilizadas são:

| Tabela | Descrição |
|---|---|
| `customers` | Dados dos clientes |
| `products` | Cadastro e informações financeiras dos produtos |
| `sessions` | Sessões de navegação |
| `events` | Eventos realizados durante as sessões |
| `orders` | Informações dos pedidos |
| `order_items` | Itens presentes nos pedidos |
| `reviews` | Avaliações dos produtos |

### Volume das bases

| Tabela | Registros |
|---|---:|
| `customers` | 20.000 |
| `products` | 1.197 |
| `sessions` | 120.000 |
| `events` | 760.958 |
| `orders` | 33.580 |
| `order_items` | 59.090 |
| `reviews` | 10.780 |

As tabelas possuem relacionamentos por meio de identificadores como `customer_id`, `session_id`, `product_id` e `order_id`.

---

## Tratamento dos dados

O tratamento foi realizado no script `02_tratamento.py`.

As principais etapas foram:

- padronização dos nomes das colunas e dados textuais;
- conversão de datas para o formato adequado;
- conversão de variáveis numéricas;
- identificação e remoção de duplicidades;
- análise dos valores ausentes;
- validação dos valores;
- validação dos identificadores;
- validação dos relacionamentos entre as tabelas.

Foram encontradas e removidas **73 linhas duplicadas na tabela `order_items`**.

Os valores ausentes da tabela `events` foram analisados considerando o tipo de evento. Alguns campos não são aplicáveis a determinados eventos e, por isso, esses valores foram mantidos.

Também foram realizadas validações de preços, custos, margens, descontos, quantidades, avaliações e consistência dos valores calculados.

### Variáveis derivadas

Durante o tratamento foram criadas três novas variáveis:

- `margin_pct`: percentual de margem do produto;
- `order_month`: mês de realização do pedido;
- `order_year`: ano de realização do pedido.

As bases tratadas foram salvas na pasta `data/processed`.

---

## Análise exploratória

A exploração dos dados foi realizada no script `01_exploracao.py`.

Foram realizadas diferentes análises para entender as características dos produtos, o comportamento das sessões e o desempenho das vendas.

### Distribuição de preços

Os produtos apresentaram preço médio de aproximadamente **US$ 119,94**, com mediana de **US$ 77,20**.

O menor preço identificado foi de **US$ 3,50** e o maior de **US$ 596,62**.

Utilizando o intervalo interquartil (IQR), foram identificados **73 possíveis outliers** acima de US$ 355,74. Esses valores não foram removidos, pois não havia evidências suficientes de que representassem erros nos dados.

### Preço e margem por categoria

`Electronics` apresentou o maior preço mediano, de **US$ 319,42**, e a maior margem mediana, de **US$ 110,18**.

`Books` apresentou o menor preço mediano, de **US$ 25,48**, e a menor margem mediana, de **US$ 8,64**.

Esses valores representam as características dos produtos e não devem ser interpretados isoladamente como medida de receita ou lucratividade total de uma categoria.

### Funil de conversão

Foram analisadas 120.000 sessões ao longo das principais etapas da jornada de compra:

| Etapa | Sessões | % do total |
|---|---:|---:|
| Page view | 120.000 | 100,00% |
| Add to cart | 81.518 | 67,93% |
| Checkout | 44.909 | 37,42% |
| Purchase | 33.580 | 27,98% |

A maior redução proporcional ocorreu entre `add_to_cart` e `checkout`, cuja taxa de passagem foi de **55,09%**.

### Conversão por fonte de tráfego

| Fonte | Sessões | Sessões com compra | Conversão |
|---|---:|---:|---:|
| Referral | 9.560 | 2.724 | 28,49% |
| Paid | 14.465 | 4.121 | 28,49% |
| Direct | 29.861 | 8.387 | 28,09% |
| Social | 14.389 | 4.024 | 27,97% |
| Email | 10.949 | 3.056 | 27,91% |
| Organic | 40.776 | 11.268 | 27,63% |

As taxas de conversão apresentaram pouca diferença entre as fontes analisadas, variando de **27,63% a 28,49%**.

### Vendas por categoria

| Categoria | Unidades vendidas | Receita (US$) |
|---|---:|---:|
| Home & Kitchen | 9.453 | 840.379,82 |
| Sports | 8.352 | 831.697,80 |
| Fashion | 10.045 | 824.307,04 |
| Electronics | 4.492 | 692.383,39 |
| Beauty | 13.313 | 691.692,89 |
| Toys | 14.861 | 568.734,90 |
| Books | 16.515 | 383.155,39 |

A análise mostra que a receita total depende tanto do valor dos produtos quanto do volume de unidades vendidas.

### Evolução mensal

Os pedidos foram agrupados por mês, totalizando **70 meses analisados**, de janeiro de 2020 a outubro de 2025.

Foram analisadas a quantidade de pedidos e a receita ao longo do período.

### Avaliações por categoria

| Categoria | Avaliações | Média |
|---|---:|---:|
| Beauty | 1.949 | 3,97 |
| Sports | 1.113 | 3,96 |
| Home & Kitchen | 1.344 | 3,95 |
| Fashion | 1.385 | 3,93 |
| Toys | 1.957 | 3,93 |
| Books | 2.341 | 3,92 |
| Electronics | 691 | 3,87 |

As avaliações médias ficaram próximas entre as categorias, variando de **3,87 a 3,97**.

---

## Dashboard

Os resultados foram apresentados em um dashboard interativo desenvolvido no **Looker Studio**.

O dashboard apresenta:

- total de pedidos;
- receita total;
- unidades vendidas;
- taxa de conversão;
- funil de conversão;
- conversão por fonte de tráfego;
- receita por categoria;
- evolução mensal da receita;
- preço e margem por categoria;
- avaliação média por categoria.

Também foram adicionados filtros para facilitar a exploração dos dados:

- **Data**
- **Categoria**
- **Fonte de tráfego**

---

## Principais insights

A análise dos dados permitiu observar alguns pontos importantes:

- Foram analisadas **120.000 sessões** e **33.580 pedidos**.
- A taxa geral de conversão do funil foi de **27,98%**.
- A maior queda proporcional ocorreu entre a adição ao carrinho e o checkout.
- As fontes de tráfego apresentaram taxas de conversão próximas.
- `Home & Kitchen` apresentou a maior receita total entre as categorias.
- `Electronics` apresentou os maiores valores de preço e margem por produto.
- `Books` apresentou o menor preço e a menor margem mediana.
- As avaliações médias das categorias ficaram próximas de 4 pontos.
- O volume de unidades vendidas possui influência importante na receita total, além do preço dos produtos.

---

## Tecnologias utilizadas

- Python
- Pandas
- Matplotlib
- Looker Studio
- CSV

---

## Estrutura do projeto

```text
ProjetoFinal/
│
├── data/
│   ├── raw/
│   │   └── dados originais
│   │
│   └── processed/
│       ├── customers_processed.csv
│       ├── products_processed.csv
│       ├── sessions_processed.csv
│       ├── events_processed.csv
│       ├── orders_processed.csv
│       ├── order_items_processed.csv
│       ├── reviews_processed.csv
│       │
│       └── analysis/
│           ├── analise_funil.csv
│           ├── analise_canais.csv
│           ├── analise_categorias.csv
│           ├── analise_preco_margem.csv
│           ├── analise_mensal.csv
│           └── analise_reviews_categoria.csv
│
├── scripts/
│   ├── 01_exploracao.py
│   ├── 02_tratamento.py
│   └── 03_analise.py
│
└── README.md
```

---

## Scripts

### `01_exploracao.py`

Responsável pela exploração inicial das bases, análise das estruturas, identificação das variáveis, validação dos relacionamentos e realização das análises exploratórias.

### `02_tratamento.py`

Responsável pela limpeza e preparação dos dados, incluindo padronização, conversão de tipos, tratamento dos valores ausentes, remoção de duplicidades, validações e criação das variáveis derivadas.

### `03_analise.py`

Responsável pelas análises finais e pela geração das tabelas agregadas e gráficos utilizados no dashboard.

---

## Conclusão

O projeto percorre as principais etapas de um processo de análise de dados: exploração, tratamento, análise e visualização.

A utilização de diferentes tabelas relacionadas possibilitou analisar o e-commerce sob diferentes perspectivas, combinando informações sobre clientes, sessões, eventos, produtos, pedidos e avaliações.

Os resultados foram organizados em tabelas analíticas e apresentados em um dashboard interativo no Looker Studio.
