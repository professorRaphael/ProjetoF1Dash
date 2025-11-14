from __future__ import annotations

from dash import Input, Output, dash_table, html
import plotly.express as px
import pandas as pd

from model.f1_model import F1DataModel


def register_callbacks(app, model: F1DataModel) -> None:
    """Registra todos os callbacks da aplicação Dash."""

    # -------- Atualiza lista de corridas quando muda o ano --------
    @app.callback(
        [Output("race-dropdown", "options"), Output("race-dropdown", "value")],
        Input("year-dropdown", "value"),
    )
    def update_race_options(year):
        if year is None:
            return [], None

        races_df = model.get_races_for_year(year)
        if races_df.empty:
            return [], None

        options = [
            {
                "label": f"{int(row['round'])} - {row['name']}",
                "value": int(row["raceId"]),
            }
            for _, row in races_df.iterrows()
        ]
        return options, options[0]["value"]

    # -------- Classificação de pilotos --------
    @app.callback(
        Output("graph-driver-standings", "figure"),
        Input("year-dropdown", "value"),
    )
    def update_driver_standings(year):
        if year is None:
            return px.bar(title="Selecione um ano.")

        df = model.get_driver_championship_standings(year)
        if df.empty:
            return px.bar(title=f"Sem dados de classificação de pilotos para {year}.")

        fig = px.bar(
            df,
            x="driverLabel",
            y="points",
            hover_data=["wins", "position"],
            title=f"Campeonato de Pilotos - {year}",
            labels={"driverLabel": "Piloto", "points": "Pontos"},
        )
        fig.update_layout(xaxis={"categoryorder": "total descending"})
        return fig

    # -------- Classificação de construtores --------
    @app.callback(
        Output("graph-constructor-standings", "figure"),
        Input("year-dropdown", "value"),
    )
    def update_constructor_standings(year):
        df = model.get_constructor_championship_standings(year)
        if df.empty:
            return px.bar(title="Sem dados de classificação de construtores.")

        fig = px.bar(
            df,
            x="name",
            y="points",
            hover_data=["wins", "position"],
            title=f"Campeonato de Construtores - {year}",
            labels={"name": "Construtor", "points": "Pontos"},
        )
        fig.update_layout(xaxis={"categoryorder": "total descending"})
        return fig

    # -------- Atualiza lista de pilotos da corrida --------
    @app.callback(
        [Output("driver-dropdown", "options"), Output("driver-dropdown", "value")],
        Input("race-dropdown", "value"),
    )
    def update_driver_options(race_id):
        if race_id is None:
            return [], None

        res = model.get_race_results(race_id)
        if res.empty:
            return [], None

        res = res.sort_values("positionOrder")
        options = [
            {
                "label": f"{row['driverLabel']} ({row['name']})",
                "value": int(row["driverId"]),
            }
            for _, row in res.iterrows()
        ]
        return options, options[0]["value"]

    # -------- Gráfico de resultados da corrida + tabela --------
    @app.callback(
        [
            Output("graph-race-results", "figure"),
            Output("table-race-results", "children"),
        ],
        Input("race-dropdown", "value"),
    )
    def update_race_results(race_id):
        if race_id is None:
            return px.bar(title="Selecione uma corrida."), html.P("")

        res = model.get_race_results(race_id)
        if res.empty:
            return px.bar(title="Sem resultados para esta corrida."), html.P(
                "Nenhum dado encontrado."
            )

        # Gráfico: grid x posição final
        fig = px.scatter(
            res,
            x="grid",
            y="positionOrder",
            text="driverLabel",
            color="name",
            title="Grid x Posição final (quanto mais baixo, melhor)",
            labels={
                "grid": "Posição no grid",
                "positionOrder": "Posição final",
                "name": "Construtor",
            },
        )
        fig.update_yaxes(autorange="reversed")  # 1 em cima

        # Tabela com info resumida
        status_col = "statusText" if "statusText" in res.columns else "statusId"
        table_cols = [
            "positionOrder",
            "driverLabel",
            "name",
            "grid",
            "points",
            "laps",
            status_col,
        ]
        table_cols = [c for c in table_cols if c in res.columns]
        res_table = res[table_cols].sort_values("positionOrder")

        table = dash_table.DataTable(
            columns=[{"name": c, "id": c} for c in res_table.columns],
            data=res_table.to_dict("records"),
            page_size=20,
            style_table={"overflowX": "auto"},
        )

        return fig, table

    # -------- Status da corrida --------
    @app.callback(
        Output("graph-status-race", "figure"),
        Input("race-dropdown", "value"),
    )
    def update_status_race(race_id):
        if race_id is None:
            return px.bar(title="Selecione uma corrida.")

        df = model.get_status_counts_for_race(race_id)
        if df.empty:
            return px.bar(title="Sem informações de status para esta corrida.")

        fig = px.bar(
            df,
            x="statusText",
            y="Count",
            title="Status dos pilotos na corrida",
            labels={"statusText": "Status", "Count": "Número de pilotos"},
        )
        fig.update_layout(xaxis={"categoryorder": "total descending"})
        return fig

    # -------- Tempos de volta --------
    @app.callback(
        Output("graph-lap-times", "figure"),
        [Input("race-dropdown", "value"), Input("driver-dropdown", "value")],
    )
    def update_lap_times(race_id, driver_id):
        if race_id is None or driver_id is None:
            return px.line(title="Selecione corrida e piloto.")

        laps = model.get_lap_times_for_driver(race_id, driver_id)
        if laps.empty:
            return px.line(title="Sem tempos de volta para este piloto/corrida.")

        fig = px.line(
            laps,
            x="lap",
            y="milliseconds",
            title="Tempo de volta por volta",
            labels={"lap": "Volta", "milliseconds": "Tempo (ms)"},
        )
        return fig

    # -------- Pit stops --------
    @app.callback(
        Output("graph-pitstops", "figure"),
        Input("race-dropdown", "value"),
    )
    def update_pitstops(race_id):
        if race_id is None:
            return px.bar(title="Selecione uma corrida.")

        pits = model.get_pitstops_for_race(race_id)
        if pits.empty:
            return px.bar(title="Nenhuma parada de box registrada.")

        counts = pits.groupby("driverId").size().reset_index(name="pit_count")

        counts = counts.merge(model.drivers, on="driverId", how="left")

        def label(row):
            if pd.notna(row.get("code")):
                return row["code"]
            if pd.notna(row.get("forename")) and pd.notna(row.get("surname")):
                return f"{row['forename'][0]}. {row['surname']}"
            return str(row.get("driverId"))

        counts["driverLabel"] = counts.apply(label, axis=1)

        fig = px.bar(
            counts,
            x="driverLabel",
            y="pit_count",
            title="Número de paradas de box por piloto",
            labels={"driverLabel": "Piloto", "pit_count": "Paradas"},
        )
        fig.update_layout(xaxis={"categoryorder": "total descending"})
        return fig

    # -------- Resultados da sprint --------
    @app.callback(
        Output("graph-sprint-results", "figure"),
        Input("race-dropdown", "value"),
    )
    def update_sprint_results(race_id):
        if race_id is None:
            return px.bar(title="Selecione uma corrida.")

        sr = model.get_sprint_results_for_race(race_id)
        if sr.empty:
            return px.bar(title="Não há sprint associada a esta corrida.")

        fig = px.bar(
            sr,
            x="driverLabel",
            y="points",
            title="Pontos da sprint por piloto",
            labels={"driverLabel": "Piloto", "points": "Pontos na sprint"},
        )
        fig.update_layout(xaxis={"categoryorder": "total descending"})
        return fig

    # -------- Visão histórica: corridas por temporada --------
    @app.callback(
        Output("graph-races-per-season", "figure"),
        Input("year-dropdown", "value"),  # usado só para disparar atualização
    )
    def update_races_per_season(_year):
        df = model.get_races_per_season()
        if df.empty:
            return px.line(title="Sem dados de temporadas.")

        fig = px.line(
            df,
            x="year",
            y="raceCount",
            title="Número de corridas por temporada",
            markers=True,
            labels={"year": "Ano", "raceCount": "Número de corridas"},
        )
        return fig

    # -------- Corridas por país no ano --------
    @app.callback(
        Output("graph-races-by-country", "figure"),
        Input("year-dropdown", "value"),
    )
    def update_races_by_country(year):
        df = model.get_race_counts_by_country(year)
        if df.empty:
            return px.bar(title="Sem dados de corridas por país para este ano.")

        title = f"Corridas por país - {year}" if year else "Corridas por país"
        fig = px.bar(
            df,
            x="country",
            y="raceCount",
            title=title,
            labels={"country": "País", "raceCount": "Número de corridas"},
        )
        fig.update_layout(xaxis={"categoryorder": "total descending"})
        return fig

    # -------- Mapa de circuitos --------
    @app.callback(
        Output("graph-circuits-map", "figure"),
        Input("year-dropdown", "value"),  # só para reagir quando o ano muda
    )

    def update_circuits_map(_year):
        df = model.get_circuit_locations()
        if df.empty:
            return px.scatter_geo(title="Sem dados de circuitos para exibir.")

        fig = px.scatter_geo(
            df,
            lat="lat",
            lon="lng",
            hover_name="circuitName",
            hover_data=["country", "location", "raceCount"],
            size="raceCount",
            title="Circuitos de F1 (tamanho = nº de corridas realizadas)",
        )
        return fig
