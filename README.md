# Dashboard Fórmula 1 com Dash (Ergast / Kaggle)

Este projeto é uma reimplementação em **Dash** de um dashboard de análise de dados originalmente feito em **Streamlit**, agora usando como base um conjunto de dados de **Fórmula 1** (derivado do _Ergast API_ via Kaggle).

O objetivo é:

- Servir como **exemplo didático** de:
  - uso de **Dash** (layout + callbacks),
  - separação em **camadas (MVC-like)**: `model/`, `view/`, `controller/`,
  - leitura e transformação de múltiplos arquivos CSV;
- Permitir explorar diversos aspectos da F1:
  - campeonatos de pilotos e construtores,
  - resultados por corrida,
  - tempos de volta, pit-stops, sprints,
  - status de abandono,
  - visão histórica de número de corridas,
  - corridas por país e mapa de circuitos.

---

## 📁 Estrutura do Projeto

```text
ProjetoMercadoDash/
├── app.py
├── requirements.txt
├── data/
│   ├── circuits.csv
│   ├── constructor_results.csv
│   ├── constructor_standings.csv
│   ├── constructors.csv
│   ├── driver_standings.csv
│   ├── drivers.csv
│   ├── lap_times.csv
│   ├── pit_stops.csv
│   ├── qualifying.csv
│   ├── races.csv
│   ├── results.csv
│   ├── seasons.csv
│   ├── sprint_results.csv
│   └── status.csv
├── model/
│   └── f1_model.py
├── view/
│   └── layout.py
└── controller/
    └── callbacks.py
````

### Camadas (MVC-like)

- **Model (`model/f1_model.py`)**

  - Responsável por:

    - carregar todos os CSVs,
    - limpar dados (`\N` → `NaN`),
    - expor métodos de consulta de alto nível, como:

      - `get_years()`
      - `get_races_for_year(year)`
      - `get_driver_championship_standings(year)`
      - `get_constructor_championship_standings(year)`
      - `get_race_results(race_id)`
      - `get_lap_times_for_driver(race_id, driver_id)`
      - `get_pitstops_for_race(race_id)`
      - `get_status_counts_for_race(race_id)`
      - `get_sprint_results_for_race(race_id)`
      - `get_races_per_season()`
      - `get_race_counts_by_country(year)`
      - `get_circuit_locations()`

- **View (`view/layout.py`)**

  - Define o **layout da aplicação Dash**:

    - dropdown de ano,
    - dropdown de corrida,
    - dropdown de piloto,
    - gráficos organizados em seções:

      - campeonatos,
      - corrida selecionada,
      - voltas e pit stops,
      - sprint,
      - tabela da corrida,
      - visão histórica,
      - visão geográfica.

- **Controller (`controller/callbacks.py`)**

  - Onde ficam os **callbacks do Dash**:

    - lê os valores dos componentes de input (dropdowns),
    - chama o `F1DataModel`,
    - devolve `figures` e tabelas para os componentes de output (gráficos, tabelas).

---

## ⚙️ Instalação

Requisitos:

- Python 3.10+ (idealmente 3.11 ou 3.12)
- `pip` instalado

1. Clone o repositório ou copie os arquivos para uma pasta:

    ```bash
    git clone https://github.com/seu-usuario/ProjetoMercadoDash.git
    cd ProjetoMercadoDash
    ```

2. Crie e ative um ambiente virtual (opcional, mas recomendado):

    ```bash
    python -m venv .venv
    # Windows:
    .venv\Scripts\activate
    # Linux/Mac:
    source .venv/bin/activate
    ```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

---

## ▶️ Execução

1. Certifique-se de que todos os arquivos CSV estão dentro da pasta `data/` com os nomes esperados.

2. Rode o app:

    ```bash
    python app.py
    ```

3. Acesse no navegador:

-* `http://127.0.0.1:8050/` (ou o host/porta que você configurou em `app.run()`).

---

## 📊 Funcionalidades do Dashboard

### Filtros

- **Ano (Season)**
  Seleciona o ano da temporada (ex.: 2021, 2022, 2023…).

- **Corrida (Race)**
  Lista todas as corridas daquele ano no formato:
  `round - nome da corrida` (ex.: `1 - Bahrain Grand Prix`).

- **Piloto (para análise de voltas)**
  Populado automaticamente com os pilotos participantes da corrida selecionada.

---

### Seções Principais

1. **Campeonato de Pilotos e Construtores**

   - Dois gráficos de barras:

     - `Campeonato de Pilotos - [ano]`
     - `Campeonato de Construtores - [ano]`
   - Dados extraídos a partir da última corrida da temporada (classificação final).

2. **Resultados da Corrida Selecionada**

   - Gráfico de dispersão:

     - eixo X: posição no grid,
     - eixo Y: posição final (quanto menor, melhor),
     - cor: construtor.
   - Tabela com:

     - posição final,
     - piloto,
     - construtor,
     - grid,
     - pontos,
     - voltas,
     - status (Finished, Accident, Engine, etc.).

3. **Status dos Pilotos na Corrida**

   - Gráfico de barras com contagem de status:

     - Finished, Accident, Collision, Engine…

4. **Tempos de Volta (Piloto Selecionado)**

   - Gráfico de linha:

     - eixo X: número da volta,
     - eixo Y: tempo em milissegundos.

5. **Paradas de Box**

   - Gráfico de barras:

     - número de pit stops por piloto na corrida.

6. **Resultados da Sprint (se houver)**

   - Gráfico de barras:

     - pontos obtidos na sprint por piloto.

7. **Número de Corridas por Temporada**

   - Gráfico de linha:

     - ano × quantidade de corridas,
     - bom para ver a evolução histórica do calendário.

8. **Corridas por País (no ano selecionado)**

   - Gráfico de barras com:

     - país × quantidade de GPs naquele ano.

9. **Mapa de Circuitos**

   - `scatter_geo` com:

     - posição geográfica de cada circuito,
     - tamanho do marcador proporcional ao nº de corridas realizadas ali.

---

## 🧑‍🏫 Uso Didático (Sugestões)

Este projeto foi pensado para ser usado em aula para ensinar:

### 2. Arquitetura em Camadas (MVC-like)

- Exercício 1 – **Model**:

  - Adicionar um método, por exemplo:

    - `get_points_evolution_for_driver(driver_id)`
      (e plotar um gráfico de pontos por corrida)
- Exercício 2 – **View**:

  - Criar uma nova seção no layout para “Análise de um piloto”.
-* Exercício 3 – **Controller**:

  -* Criar callbacks que liguem um novo dropdown de piloto a esse novo gráfico.

### 3. Data Wrangling com Pandas

-* Explorar junções entre:

- `results + drivers + constructors + status`,
  - `races + circuits`,
  -* `sprint_results` vs. `results`.

---

## 🚀 Possíveis Extensões

Algumas ideias de extensões para projetos/trabalhos:

- Comparar desempenho de dois pilotos ao longo do ano (side-by-side).
- Criar um “driver profile” com:

  - vitórias, pódios, poles, voltas rápidas.
- Adicionar filtros por:

  - tipo de circuito (rua vs permanente),
  - país ou continente.
- Fazer análises de:

  - correlação entre posição no grid e resultado final,
  - impacto de pit stops na posição final.

---

## 📝 Licença

Projeto para fins acadêmicos/didáticos.
Os dados de Fórmula 1 são derivados da _Ergast API_ (via Kaggle) e devem respeitar os termos de uso da respectiva fonte.
