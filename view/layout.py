from __future__ import annotations

from dash import dcc, html

from model.f1_model import F1DataModel


def create_layout(model: F1DataModel) -> html.Div:
    """
    Constrói o layout principal da aplicação Dash.

    Os filtros são baseados em:
      - Ano (season)
      - Corrida (race)
      - Piloto (para análise de voltas)
    """

    years = model.get_years()
    default_year = years[-1] if years else None

    races_df = model.get_races_for_year(default_year) if default_year else None

    race_options = []
    default_race = None
    if races_df is not None and not races_df.empty:
        race_options = [
            {
                "label": f"{int(row['round'])} - {row['name']}",
                "value": int(row["raceId"]),
            }
            for _, row in races_df.iterrows()
        ]
        default_race = race_options[0]["value"]

    return html.Div(
        [
            html.H1("Dashboard Fórmula 1 (Ergast)"),
            html.P(
                "Explore campeonatos, resultados de corridas, tempos de volta, "
                "paradas de box, sprints, status e visão histórica das temporadas."
            ),
            # -------- Filtros superiores --------
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Ano"),
                            dcc.Dropdown(
                                id="year-dropdown",
                                options=[{"label": str(y), "value": y} for y in years],
                                value=default_year,
                                clearable=False,
                            ),
                        ],
                        style={"width": "20%", "display": "inline-block"},
                    ),
                    html.Div(
                        [
                            html.Label("Corrida"),
                            dcc.Dropdown(
                                id="race-dropdown",
                                options=race_options,
                                value=default_race,
                                clearable=False,
                            ),
                        ],
                        style={
                            "width": "50%",
                            "display": "inline-block",
                            "marginLeft": "2%",
                        },
                    ),
                    html.Div(
                        [
                            html.Label("Piloto (para análise de voltas)"),
                            dcc.Dropdown(
                                id="driver-dropdown",
                                options=[],
                                value=None,
                                placeholder="Selecione uma corrida primeiro",
                            ),
                        ],
                        style={
                            "width": "25%",
                            "display": "inline-block",
                            "marginLeft": "2%",
                        },
                    ),
                ],
                style={"marginBottom": "20px"},
            ),
            html.Hr(),
            # -------- Linha 1: campeonatos --------
            html.Div(
                [
                    html.Div(
                        [dcc.Graph(id="graph-driver-standings")],
                        style={"width": "48%", "display": "inline-block"},
                    ),
                    html.Div(
                        [dcc.Graph(id="graph-constructor-standings")],
                        style={
                            "width": "48%",
                            "display": "inline-block",
                            "float": "right",
                        },
                    ),
                ]
            ),
            # -------- Linha 2: corrida --------
            html.Div(
                [
                    html.H3("Resultados da corrida selecionada"),
                    dcc.Graph(id="graph-race-results"),
                ],
                style={"marginTop": "40px"},
            ),
            html.Div(
                [
                    html.H3("Status dos pilotos na corrida"),
                    dcc.Graph(id="graph-status-race"),
                ],
                style={"marginTop": "20px"},
            ),
            # -------- Linha 3: voltas e pits --------
            html.Div(
                [
                    html.Div(
                        [
                            html.H3("Tempos de volta do piloto"),
                            dcc.Graph(id="graph-lap-times"),
                        ],
                        style={"width": "48%", "display": "inline-block"},
                    ),
                    html.Div(
                        [
                            html.H3("Paradas de box por piloto"),
                            dcc.Graph(id="graph-pitstops"),
                        ],
                        style={
                            "width": "48%",
                            "display": "inline-block",
                            "float": "right",
                        },
                    ),
                ],
                style={"marginTop": "40px"},
            ),
            # -------- Linha 4: sprint --------
            html.Div(
                [
                    html.H3("Resultados da sprint (se houver)"),
                    dcc.Graph(id="graph-sprint-results"),
                ],
                style={"marginTop": "40px"},
            ),
            # -------- Tabela --------
            html.Div(
                [
                    html.H3("Tabela de resultados da corrida"),
                    dcc.Loading(
                        id="loading-table",
                        type="default",
                        children=html.Div(id="table-race-results"),
                    ),
                ],
                style={"marginTop": "40px"},
            ),
            # -------- Visão histórica --------
            html.Div(
                [
                    html.H3("Número de corridas por temporada"),
                    dcc.Graph(id="graph-races-per-season"),
                ],
                style={"marginTop": "40px"},
            ),
            # -------- Visão geográfica --------
            html.Div(
                [
                    html.H3("Corridas por país no ano selecionado"),
                    dcc.Graph(id="graph-races-by-country"),
                ],
                style={"marginTop": "40px"},
            ),
            html.Div(
                [
                    html.H3("Mapa de circuitos (todas as temporadas)"),
                    dcc.Graph(id="graph-circuits-map"),
                ],
                style={"marginTop": "20px"},
            ),
        ],
        style={"margin": "20px"},
    )
