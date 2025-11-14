from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import pandas as pd


@dataclass
class F1DataModel:
    """Camada de acesso e transformação dos dados de Fórmula 1."""

    base_path: Path

    def __post_init__(self) -> None:
        self.races = self._load_csv("races.csv")
        self.results = self._load_csv("results.csv")
        self.drivers = self._load_csv("drivers.csv")
        self.driver_standings = self._load_csv("driver_standings.csv")
        self.constructors = self._load_csv("constructors.csv")
        self.constructor_standings = self._load_csv("constructor_standings.csv")
        self.constructor_results = self._load_csv("constructor_results.csv")
        self.lap_times = self._load_csv("lap_times.csv")
        self.pit_stops = self._load_csv("pit_stops.csv")
        self.qualifying = self._load_csv("qualifying.csv")
        self.seasons = self._load_csv("seasons.csv")
        self.status = self._load_csv("status.csv")
        self.sprint_results = self._load_csv("sprint_results.csv")
        self.circuits = self._load_csv("circuits.csv")

        # Tipagem básica
        self.races["year"] = pd.to_numeric(self.races["year"], errors="coerce")

    # ----------------- util interno -----------------

    def _load_csv(self, name: str) -> pd.DataFrame:
        path = self.base_path / name
        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {path}")
        df = pd.read_csv(path, na_values="\\N")

        # Normaliza strings '\N' como NaN
        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].replace("\\N", pd.NA)
        return df

    # ----------------- consultas para filtros -----------------

    def get_years(self) -> List[int]:
        return self.races["year"].dropna().astype(int).sort_values().unique().tolist()

    def get_races_for_year(self, year: int) -> pd.DataFrame:
        df = self.races[self.races["year"] == year].copy()
        df = df.sort_values("round")
        return df[["raceId", "name", "round"]]

    # ----------------- campeonatos -----------------

    def get_driver_championship_standings(self, year: int) -> pd.DataFrame:
        """Classificação final de pilotos em um ano."""
        races_year = self.races[self.races["year"] == year]
        if races_year.empty:
            return pd.DataFrame()

        race_ids = races_year["raceId"]
        ds = self.driver_standings[
            self.driver_standings["raceId"].isin(race_ids)
        ].copy()
        if ds.empty:
            return pd.DataFrame()

        ds.loc[:, "raceId"] = pd.to_numeric(ds["raceId"], errors="coerce")
        idx = ds.groupby("driverId")["raceId"].idxmax()
        final_ds = ds.loc[idx].copy()

        final_ds = final_ds.merge(self.drivers, on="driverId", how="left")

        def label(row):
            if pd.notna(row.get("code")):
                return row["code"]
            if pd.notna(row.get("forename")) and pd.notna(row.get("surname")):
                return f"{row['forename'][0]}. {row['surname']}"
            return str(row.get("driverId"))

        final_ds["driverLabel"] = final_ds.apply(label, axis=1)

        for col in ["points", "wins", "position"]:
            if col in final_ds.columns:
                final_ds[col] = pd.to_numeric(final_ds[col], errors="coerce")

        return final_ds.sort_values(["points", "wins"], ascending=[False, False])

    def get_constructor_championship_standings(self, year: int) -> pd.DataFrame:
        """Classificação final de construtores em um ano."""
        races_year = self.races[self.races["year"] == year]
        if races_year.empty:
            return pd.DataFrame()

        race_ids = races_year["raceId"]
        cs = self.constructor_standings[
            self.constructor_standings["raceId"].isin(race_ids)
        ].copy()
        if cs.empty:
            return pd.DataFrame()

        cs.loc[:, "raceId"] = pd.to_numeric(cs["raceId"], errors="coerce")
        idx = cs.groupby("constructorId")["raceId"].idxmax()
        final_cs = cs.loc[idx].copy()

        final_cs = final_cs.merge(self.constructors, on="constructorId", how="left")

        for col in ["points", "wins", "position"]:
            if col in final_cs.columns:
                final_cs[col] = pd.to_numeric(final_cs[col], errors="coerce")

        return final_cs.sort_values(["points", "wins"], ascending=[False, False])

    # ----------------- corrida específica -----------------

    def get_race_results(self, race_id: int) -> pd.DataFrame:
        """Resultados completos de uma corrida, com status textual."""
        res = self.results[self.results["raceId"] == race_id].copy()
        if res.empty:
            return pd.DataFrame()

        for col in ["grid", "positionOrder", "points", "laps"]:
            if col in res.columns:
                res[col] = pd.to_numeric(res[col], errors="coerce")

        # Junta com pilotos
        res = res.merge(self.drivers, on="driverId", how="left")
        # Junta com construtores
        res = res.merge(
            self.constructors,
            on="constructorId",
            how="left",
            suffixes=("", "_constructor"),
        )

        # Junta com tabela de status para ter texto (DNF, Accident, etc.)
        if "statusId" in res.columns and not self.status.empty:
            status_df = self.status.copy()
            status_df["statusId"] = pd.to_numeric(
                status_df["statusId"], errors="coerce"
            )
            res["statusId"] = pd.to_numeric(res["statusId"], errors="coerce")
            res = res.merge(
                status_df[["statusId", "status"]],
                on="statusId",
                how="left",
            )
            res = res.rename(columns={"status": "statusText"})

        def label(row):
            if pd.notna(row.get("code")):
                return row["code"]
            if pd.notna(row.get("forename")) and pd.notna(row.get("surname")):
                return f"{row['forename'][0]}. {row['surname']}"
            return str(row.get("driverId"))

        res["driverLabel"] = res.apply(label, axis=1)
        return res

    def get_lap_times_for_driver(self, race_id: int, driver_id: int) -> pd.DataFrame:
        """Tempos de volta de um piloto em uma corrida."""
        laps = self.lap_times[
            (self.lap_times["raceId"] == race_id)
            & (self.lap_times["driverId"] == driver_id)
        ].copy()
        if laps.empty:
            return pd.DataFrame()

        laps["milliseconds"] = pd.to_numeric(laps["milliseconds"], errors="coerce")
        laps = laps.sort_values("lap")
        return laps

    def get_pitstops_for_race(self, race_id: int) -> pd.DataFrame:
        """Paradas de box por corrida."""
        pits = self.pit_stops[self.pit_stops["raceId"] == race_id].copy()
        if pits.empty:
            return pd.DataFrame()

        pits["milliseconds"] = pd.to_numeric(pits["milliseconds"], errors="coerce")
        return pits

    # -----------------  status e sprint -----------------

    def get_status_counts_for_race(self, race_id: int) -> pd.DataFrame:
        """Contagem de status (Finished, Accident, Engine...) em uma corrida."""
        res = self.get_race_results(race_id)
        if res.empty or "statusText" not in res.columns:
            return pd.DataFrame()

        grouped = (
            res.groupby("statusText")
            .size()
            .reset_index(name="Count")
            .sort_values("Count", ascending=False)
        )
        return grouped

    def get_sprint_results_for_race(self, race_id: int) -> pd.DataFrame:
        """Resultados da sprint associada à corrida (se existir)."""
        sr = self.sprint_results[self.sprint_results["raceId"] == race_id].copy()
        if sr.empty:
            return pd.DataFrame()

        # Converte colunas numéricas básicas
        for col in ["grid", "position", "positionOrder", "points", "laps"]:
            if col in sr.columns:
                sr[col] = pd.to_numeric(sr[col], errors="coerce")

        # Junta com drivers e constructors
        sr = sr.merge(self.drivers, on="driverId", how="left")
        sr = sr.merge(
            self.constructors,
            on="constructorId",
            how="left",
            suffixes=("", "_constructor"),
        )

        def label(row):
            if pd.notna(row.get("code")):
                return row["code"]
            if pd.notna(row.get("forename")) and pd.notna(row.get("surname")):
                return f"{row['forename'][0]}. {row['surname']}"
            return str(row.get("driverId"))

        sr["driverLabel"] = sr.apply(label, axis=1)
        # Ordena pela posição da sprint (positionOrder se existir, senão position)
        order_col = "positionOrder" if "positionOrder" in sr.columns else "position"
        if order_col in sr.columns:
            sr = sr.sort_values(order_col)
        return sr

    # ----------------- NOVO: visão histórica de temporadas -----------------

    def get_races_per_season(self) -> pd.DataFrame:
        """Número de corridas por temporada."""
        races_per_year = (
            self.races.groupby("year")
            .size()
            .reset_index(name="raceCount")
            .sort_values("year")
        )
        return races_per_year

    def get_race_counts_by_country(self, year: int | None = None) -> pd.DataFrame:
        """Quantidade de corridas por país (opcionalmente filtrado por ano)."""
        races = self.races.copy()
        if year is not None:
            races = races[races["year"] == year]

        if races.empty or "circuitId" not in races.columns:
            return pd.DataFrame()

        if self.circuits.empty or "circuitId" not in self.circuits.columns:
            return pd.DataFrame()

        df = races.merge(
            self.circuits[["circuitId", "country"]],
            on="circuitId",
            how="left",
        )

        grouped = (
            df.groupby("country")
            .size()
            .reset_index(name="raceCount")
            .sort_values("raceCount", ascending=False)
        )
        return grouped

    def get_circuit_locations(self) -> pd.DataFrame:
        """
        Circuitos com localização (lat/lng) e quantas corridas já receberam.
        Usa o nome do circuito (circuitName), não o nome da corrida.
        """
        if self.races.empty or self.circuits.empty:
            return pd.DataFrame()

        # Pegamos só as colunas relevantes dos circuitos
        circuits = self.circuits[
            ["circuitId", "name", "location", "country", "lat", "lng"]
        ].copy()

        # Renomeia para evitar conflito com races.name (nome do GP)
        circuits = circuits.rename(columns={"name": "circuitName"})

        # Junta corridas com info de circuito
        merged = self.races.merge(circuits, on="circuitId", how="left")

        # Agrupa para saber quantas corridas cada circuito recebeu
        grouped = (
            merged.groupby(
                ["circuitId", "circuitName", "location", "country", "lat", "lng"]
            )
            .size()
            .reset_index(name="raceCount")
        )

        # Garante que lat/lng são numéricos
        for col in ("lat", "lng"):
            grouped[col] = pd.to_numeric(grouped[col], errors="coerce")

        # Remove linhas sem coordenadas
        grouped = grouped.dropna(subset=["lat", "lng"])
        return grouped
