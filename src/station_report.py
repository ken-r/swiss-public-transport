"""Aggregate scheduled departures by station and draw a summary chart."""

import argparse
from collections import Counter
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # Render image files without a desktop display.
import matplotlib.pyplot as plt
from matplotlib.path import Path as MapPath
import pandas as pd
import requests

from .config import ANALYSIS_GTFS_COLUMNS, ANALYSIS_GTFS_DTYPES
from .load import load_gtfs_file

MAP_EXTENT = (5.8, 10.8, 45.7, 48.0)
BAR_TOP_COUNT = 12  # Fits the ranking panel without crowding the names.
HOURLY_TOP_COUNT = 5
MAP_TOP_COUNT = 500  # Limit overlapping map markers to the busiest stations.
SECONDS_PER_HOUR = 60 * 60


class StationReport:
    """Accumulate small station/hour summaries while stop times stream by."""

    def __init__(self, stops: pd.DataFrame, border: list) -> None:
        if stops["stop_id"].isna().any() or not stops["stop_id"].is_unique:
            raise ValueError("Stops contain missing or duplicate stop IDs.")
        station_ids = stops["parent_station"].fillna(stops["stop_id"])
        if not station_ids.isin(stops["stop_id"]).all():
            raise ValueError("A stop references an unknown parent station.")
        self.station_by_stop = pd.Series(station_ids.array, index=stops["stop_id"])
        self.border = border
        self.stations = swiss_stations((
            stops.set_index("stop_id")
            .loc[station_ids.unique(), ["stop_name", "stop_lat", "stop_lon"]]
            .rename_axis("station_id")
        ), border)
        self.counts: Counter[str] = Counter()
        self.hourly: Counter[tuple[str, int]] = Counter()

    @classmethod
    def from_gtfs(cls) -> "StationReport":
        """Load only the stop fields needed for grouping and the map."""
        return cls(load_gtfs_file(
            "stops", columns=ANALYSIS_GTFS_COLUMNS["stops"],
            dtype=ANALYSIS_GTFS_DTYPES["stops"],
        ), load_swiss_border())

    def add(self, departures: pd.DataFrame) -> None:
        """Count eligible departures by parent station and calendar-day hour."""
        ids = departures["stop_id"].map(self.station_by_stop)
        if ids.isna().any():
            raise ValueError("A departure references an unknown stop.")
        # A Swiss origin counts even when its trip continues abroad.
        ids = ids.loc[ids.isin(self.stations.index)]
        hours = (departures.loc[ids.index, "departure_seconds"] // SECONDS_PER_HOUR % 24).astype(int)
        self.counts.update(ids.value_counts().to_dict())
        self.hourly.update(pd.DataFrame({
            "station_id": ids, "hour": hours,
        }).value_counts().to_dict())

    def save(self, directory: str, calendar_date: date) -> None:
        """Write reproducible CSV summaries and PNG/SVG charts."""
        if not self.counts:
            raise ValueError("No scheduled departures were found for this date.")
        destination = Path(directory)
        destination.mkdir(parents=True, exist_ok=True)
        ranking = pd.DataFrame(self.counts.items(), columns=[
            "station_id", "scheduled_departures",
        ]).join(self.stations, on="station_id", validate="many_to_one")
        ranking = ranking.sort_values(
            ["scheduled_departures", "station_id"], ascending=[False, True],
        ).reset_index(drop=True)
        ranking.insert(0, "calendar_date", calendar_date.isoformat())
        ranking.to_csv(destination / "station_departures.csv", index=False)

        top_ids = set(ranking.head(HOURLY_TOP_COUNT)["station_id"])
        hourly = pd.DataFrame(
            ((station, hour, count) for (station, hour), count in self.hourly.items()
             if station in top_ids),
            columns=["station_id", "hour", "scheduled_departures"],
        ).sort_values(["station_id", "hour"])
        hourly.insert(0, "calendar_date", calendar_date.isoformat())
        hourly.to_csv(destination / "top_station_hourly.csv", index=False)
        draw_summary(ranking, hourly, destination, calendar_date, self.border)


def draw_summary(
    ranking: pd.DataFrame, hourly: pd.DataFrame, destination: Path,
    calendar_date: date, border: list | None = None,
) -> None:
    """Draw a geographic view, ranking, and hourly profiles in one image."""
    border = border if border is not None else load_swiss_border()
    ranking = swiss_stations(ranking, border)
    top = ranking.head(BAR_TOP_COUNT)
    cities = {name.split(",", 1)[0] for name in top["stop_name"]}
    fig = plt.figure(figsize=(16, 9), facecolor="#101827")
    grid = fig.add_gridspec(2, 2, width_ratios=[1.15, 1], hspace=.32, wspace=.38,
                            left=.06, right=.96, top=.83, bottom=.10)
    map_ax = fig.add_subplot(grid[:, 0])
    rank_ax = fig.add_subplot(grid[0, 1])
    hour_ax = fig.add_subplot(grid[1, 1])
    for ax in (map_ax, rank_ax, hour_ax):
        ax.set_facecolor("#182437")
        ax.tick_params(colors="#d7e3f1", labelsize=10, length=0)
        ax.xaxis.label.set_color("#d7e3f1")
        ax.yaxis.label.set_color("#d7e3f1")
        for spine in ax.spines.values():
            spine.set_visible(False)

    for polygon in border:
        for ring in polygon:
            lon, lat = zip(*ring)
            map_ax.plot(lon, lat, color="#9b75be", linewidth=1.4, zorder=1)
    region = ranking.loc[
        ranking["stop_lon"].between(MAP_EXTENT[0], MAP_EXTENT[1])
        & ranking["stop_lat"].between(MAP_EXTENT[2], MAP_EXTENT[3])
    ].head(MAP_TOP_COUNT)
    map_ax.scatter(region["stop_lon"], region["stop_lat"],
                   s=region["scheduled_departures"].clip(upper=1500) * .25 + 8,
                   c="#55d6be", alpha=.55, edgecolors="none", rasterized=True,
                   zorder=2)
    labeled_cities: set[str] = set()
    for row in region.itertuples():
        city = row.stop_name.split(",", 1)[0]
        if city not in cities or city in labeled_cities:
            continue
        map_ax.text(row.stop_lon + .07, row.stop_lat + .025, city,
                    color="white", fontsize=9)
        labeled_cities.add(city)
        if len(labeled_cities) == len(cities):
            break
    map_ax.set(xlim=MAP_EXTENT[:2], ylim=MAP_EXTENT[2:])
    map_ax.set_xticks([])
    map_ax.set_yticks([])
    map_ax.set_aspect(1.4)
    map_ax.set_title(f"TOP {len(region)} STATIONS · SWITZERLAND", color="white", loc="left",
                     fontsize=12, pad=15)

    rank_ax.barh(top.iloc[::-1]["stop_name"], top.iloc[::-1]["scheduled_departures"],
                 color="#ffbd69")
    rank_ax.set_title(f"TOP {len(top)} STATIONS · DEPARTURES", color="white", loc="left",
                      fontsize=12, pad=15)
    rank_ax.tick_params(axis="y", labelsize=8)
    rank_ax.grid(axis="x", color="white", alpha=.09)
    rank_ax.set_axisbelow(True)

    for row in ranking.head(HOURLY_TOP_COUNT).itertuples():
        series = hourly.loc[hourly["station_id"].eq(row.station_id)]
        counts = series.set_index("hour")["scheduled_departures"].reindex(
            range(24), fill_value=0,
        )
        hour_ax.plot(counts.index, counts,
                     marker="o", markersize=2, linewidth=2, label=row.stop_name)
    hour_ax.set(xlim=(0, 23), xlabel="Time of day", ylabel="Departures")
    hour_ax.set_xticks(range(0, 24, 3), [f"{hour:02d}:00" for hour in range(0, 24, 3)])
    hour_ax.set_title(f"TOP {HOURLY_TOP_COUNT} · DEPARTURES BY HOUR", color="white", loc="left",
                      fontsize=12, pad=15)
    hour_ax.grid(color="white", alpha=.09)
    hour_ax.legend(frameon=False, labelcolor="white", fontsize=8, ncol=2)

    fig.text(.06, .94, "SWISS PUBLIC TRANSPORT", color="white",
             fontsize=27, weight="bold")
    fig.text(.06, .89, f"Scheduled departures · {calendar_date.strftime('%d %B %Y')}",
             color="#a9b9cb", fontsize=14)
    fig.text(.06, .035, "Source: opentransportdata.swiss GTFS · Border: swisstopo swissBOUNDARIES3D · Scheduled counts, not passengers or actual traffic",
             color="#a9b9cb", fontsize=9)
    for extension in ("png", "svg"):
        fig.savefig(destination / f"station_connectivity.{extension}", dpi=180,
                    facecolor=fig.get_facecolor())
    plt.close(fig)


def load_swiss_border() -> list:
    """Fetch only Switzerland's official WGS84 polygon from swisstopo."""
    params = {
        "layer": "ch.swisstopo.swissboundaries3d-land-flaeche.fill",
        "searchText": "CH", "searchField": "id", "contains": "false",
        "geometryFormat": "geojson", "sr": 4326,
    }
    response = requests.get("https://api3.geo.admin.ch/rest/services/ech/MapServer/find",
                            params=params,
                            timeout=15)
    response.raise_for_status()
    results = response.json()["results"]
    if len(results) != 1 or results[0]["id"] != "CH":
        raise ValueError("swisstopo did not return the Swiss border.")
    geometry = results[0]["geometry"]
    if geometry["type"] != "MultiPolygon":
        raise ValueError("Unexpected Swiss border geometry.")
    return geometry["coordinates"]


def swiss_stations(ranking: pd.DataFrame, border: list) -> pd.DataFrame:
    """Keep station coordinates inside Swiss polygons, excluding their holes."""
    points = ranking[["stop_lon", "stop_lat"]].to_numpy()
    inside = pd.Series(False, index=ranking.index)
    for polygon in border:
        polygon_inside = MapPath(polygon[0]).contains_points(points)
        for hole in polygon[1:]:
            polygon_inside &= ~MapPath(hole).contains_points(points)
        inside |= polygon_inside
    return ranking.loc[inside]


def main() -> None:
    """Redraw the figure from saved summaries without reprocessing GTFS files."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-dir", type=Path, required=True)
    directory = parser.parse_args().report_dir
    ranking = pd.read_csv(directory / "station_departures.csv",
                          dtype={"station_id": "string"})
    hourly = pd.read_csv(directory / "top_station_hourly.csv",
                         dtype={"station_id": "string"})
    calendar_date = date.fromisoformat(ranking["calendar_date"].iloc[0])
    draw_summary(ranking, hourly, directory, calendar_date)


if __name__ == "__main__":
    main()
