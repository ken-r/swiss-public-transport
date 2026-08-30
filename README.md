# Swiss Transport Data Project

This project explores Swiss public transport data using the GTFS dataset provided by the Swiss Mobility Open Data Platform [opentransportdata.swiss](https://opentransportdata.swiss).

This project uses [Docker](https://www.docker.com/) to keep the setup clean and reproducible. If you have not installed it yet, please follow the instructions [here](https://docs.docker.com/desktop/setup/install).

## Data Information

|  |  |
|---|---|
| **Source** | Swiss Mobility Open Data Platform ([opentransportdata.swiss](https://opentransportdata.swiss)) |
| **Link** | [GTFS 2026 dataset](https://data.opentransportdata.swiss/dataset/timetable-2026-gtfs2020/resource_permalink/gtfs_fp2026_20260815.zip) |
| **Dataset** | `GTFS_FP2026_20260815.zip` |
| **Downloaded** | 2026-08-19 |

High-level documentation about the GTFS dataset can be found [here](https://opentransportdata.swiss/en/cookbook/timetable-cookbook/gtfs/). Technical documenation, including the description of all data files and field descriptions can be found [here](https://gtfs.org/documentation/schedule/reference/).

## Setup

1. Download the GTFS dataset from the link above.
2. Store the extracted contents in `data/raw/gtfs`.
3. Build the Docker image: 
    ```bash 
    docker compose build
    ```

## Run

Run the GTFS inspection script with
```bash
docker compose run --rm app
```
