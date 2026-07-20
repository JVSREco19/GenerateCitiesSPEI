# 🌍 GenerateCitiesSPEI

> **A clean, object-oriented Python pipeline that turns a gridded SPEI drought index into per-municipality Excel time series for the *Norte de Minas Gerais* region of Brazil.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![pandas](https://img.shields.io/badge/pandas-DataFrame-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Last commit](https://img.shields.io/badge/last--commit-Jul%202026-blue)](#-project-status)

---

## 📌 What is this?

`GenerateCitiesSPEI` is a small but well-structured **data-preparation tool** designed as a precursor to a downstream **drought-prediction model** (an LSTM-based system, in our case). It solves a single recurring problem in climate-impact studies:

> *"I have a high-resolution SPEI gridded dataset, but I need the time series **for the exact coordinate of a given city** — and, ideally, also for every city that borders it."*

The pipeline reads a national Excel sheet of Brazilian municipality coordinates, narrows it down to a hand-picked set of *"central"* municipalities and their *bordering* neighbors in the **North of Minas Gerais** (state code **31**), finds the **closest gridded SPEI measurement point** to each one using Euclidean distance, and writes one tidy `.xlsx` file per city into a per-central-city folder under `Data/`.

It is intentionally written in a **modular, class-based style** so that adding a new state, a new index (SPI, PDSI, …) or a new output format is a matter of swapping one class — not rewriting the script.

---

## ✨ Features

- 🧭 **State-scoped filtering** — keeps only municipalities whose `GEOCODIGO_MUNICIPIO` starts with a configurable state code (default `31` = Minas Gerais).
- 🎯 **City-set filtering** — keeps only the municipalities listed in `cidades.json` (central + bordering).
- 📐 **Nearest-neighbor matching** — for every kept city, finds the closest SPEI grid point by Euclidean distance on `(latitude, longitude)`.
- 📊 **Per-city time series** — extracts a `(date, SPEI)` time series for each city and writes it to an `.xlsx` file.
- 📁 **Organized output** — files are grouped under `Data/<CENTRAL_CITY>/<city_name>.xlsx`, so each central city is its own self-contained deliverable.
- 🧱 **Clean OOP architecture** — five small, single-purpose classes, each in its own file under `classes/`.
- 🔡 **Unicode-safe** — handles Portuguese accents (`São João da Ponte`, `Janaúba`, `Pintópolis`, …) end-to-end.

---

## 🗂️ Project Structure

```
GenerateCitiesSPEI/
├── main.py                          # Pipeline entry point
├── cidades.json                     # Central cities → bordering cities map
├── CoordenadasMunicipios.xlsx       # National municipality-coordinates table
├── speiAll_final.csv                # Gridded SPEI time series (header = "X,lon,lat")
├── classes/                         # OOP building blocks
│   ├── __init__.py
│   ├── city_directory.py            # CityDirectory
│   ├── chosen_cities_index.py       # ChosenCitiesIndex
│   ├── spei_directory.py            # SPEIDirectory
│   ├── nearest_locator.py           # NearestLocator
│   └── file_writer.py               # FileWriter
├── Data/                            # Generated .xlsx output (gitignored)
│   ├── ESPINOSA/
│   │   ├── ESPINOSA.xlsx
│   │   ├── GAMELEIRAS.xlsx
│   │   └── …
│   ├── LASSANCE/
│   ├── RIO PARDO DE MINAS/
│   ├── SÃO FRANCISCO/
│   └── SÃO JOÃO DA PONTE/
└── .gitignore
```

---

## 📥 Inputs

| File | Format | Used for |
| --- | --- | --- |
| `CoordenadasMunicipios.xlsx` | Excel, indexed by `GEOCODIGO_MUNICIPIO` | Source of truth for municipality **name → (LATITUDE, LONGITUDE)** |
| `speiAll_final.csv` | `;`-delimited CSV, `,` decimal, indexed by `Dates`; columns named `X,<lon>,<lat>` | Source of the SPEI gridded time series |
| `cidades.json` | JSON: `central_city → [bordering_cities]` | Defines the cities of interest |

### `cidades.json` at a glance

Five central municipalities in the *Norte de Minas* are currently tracked, each with its list of neighboring cities:

- **Espinosa** (5 neighbors)
- **Rio Pardo de Minas** (14 neighbors)
- **São Francisco** (8 neighbors)
- **São João da Ponte** (9 neighbors)
- **Lassance** (3 neighbors)

Total: **5 central + 39 bordering = 44 cities** whose SPEI time series are produced on each run.

---

## 📤 Outputs

For every **central city** in `cidades.json`, the pipeline creates:

```
Data/<CENTRAL_CITY>/
├── <CENTRAL_CITY>.xlsx               # its own time series
└── <bordering_city_1>.xlsx          # one file per neighbor
└── …
```

Each `.xlsx` contains two columns:

| Column | Type | Description |
| --- | --- | --- |
| `Dates` (index) | `datetime` | Monthly timestamp (1st of each month) |
| `Series 1` | `float` | SPEI value at the nearest grid point to the city |

A typical file spans **1962-01 → 2020-01** (~700 monthly rows, ~21 kB).

---

## 🧠 How the algorithm works

The flow is intentionally simple and linear — five classes, one job each:

### 1. `CityDirectory` — *where are the cities?*
1. Loads `CoordenadasMunicipios.xlsx` (indexed by `GEOCODIGO_MUNICIPIO`).
2. **`narrow_down_by_state_geocode(31)`** — keeps only Minas Gerais municipalities (`31xxxxx`) and re-indexes by `NOME_MUNICIPIO`.
3. **`narrow_down_by_city_set(...)`** — keeps only the central + bordering cities listed in `cidades.json`.

### 2. `ChosenCitiesIndex` — *which cities do we actually want?*
1. Reads `cidades.json` and flattens the `central → [bordering]` map into a `(Central, Bordering)` tuple list.
2. Upper-cases every name (matches the IBGE upper-case convention used by `CoordenadasMunicipios.xlsx`).
3. Exposes helpers: `get_chosen_cities_set()`, `get_chosen_central_cities_set()`, `get_bordering_cities_set(central)`.

### 3. `SPEIDirectory` — *what is the SPEI grid?*
1. Loads `speiAll_final.csv` (separator `;`, decimal `,`, `Dates` as index).
2. Parses every column header `X,<lon>,<lat>` back into a `(longitude, latitude)` pair via `get_col_coords`.
3. **`make_city_timeseries_df(city, df_nearest)`** — picks the column whose coordinates match the city’s nearest grid point, renames it to `Series 1`, casts the values to `float` and the index to `datetime`.

### 4. `NearestLocator` — *which grid point is the closest?*
1. Initializes an empty DataFrame with the same index as `CityDirectory.df` — one row per city, two columns `LATITUDE`/`LONGITUDE`.
2. For each city, it walks **every** SPEI grid column, computes the Euclidean distance

   $$d(\text{city}, \text{col}) = \sqrt{(\text{lat}_c - \text{lat}_g)^2 + (\text{lon}_c - \text{lon}_g)^2}$$

   and stores the coordinates of the closest one.
3. The matching helpers are split into small, testable pieces:
   - `_get_city_coords` / `_get_col_coords`
   - `_calculate_col_distances` (per-city sweep)
   - `_find_min_distance` (arg-min over the distance dict)
   - `_find_nearest_col` (glue)

> ⚠️ **Heads up — coordinate order.** `_calculate_euclidean_distance` constructs its point tuple as `(LATITUDE, LONGITUDE)`, while SPEI column headers are stored as `X,<lon>,<lat>`. For very short distances the two conventions are interchangeable up to rotation; for analytical work you may want to standardize on `(lon, lat)`.

### 5. `FileWriter` — *write the deliverables.*
1. **`create_directory(central_city)`** — `Data/<central_city>/`.
2. **`write_xlsx(df, central, name)`** — `Data/<central>/<name>.xlsx`, with the date index preserved.

---

## 🚀 Getting started

### Prerequisites

- Python **3.10+**
- `pandas`
- `numpy`
- `openpyxl` (required by `pandas.to_excel`)

### Install

```bash
git clone https://github.com/A-Infor/GenerateCitiesSPEI.git
cd GenerateCitiesSPEI
python -m venv .venv && source .venv/bin/activate
pip install pandas numpy openpyxl
```

### Run

```bash
python main.py
```

The script will print progress as it goes and leave one folder per central city inside `Data/`. On the current dataset (44 cities) the full run finishes in a few seconds.

---

## 🧩 Extending the pipeline

The class boundaries are deliberate. Some easy next steps:

| Goal | Where to change it |
| --- | --- |
| Add another **state** | Call `CityDirectory.narrow_down_by_state_geocode(<code>)` with a different `IBGE` code (`11` = RO, `35` = SP, …) |
| Track a **new set of central cities** | Edit `cidades.json`; nothing else changes |
| Switch to a **different drought index** (SPI, PDSI, SPEI-12…) | Replace the `speiAll_final.csv` file; `SPEIDirectory` is index-agnostic |
| Change the **output format** (Parquet, CSV, NetCDF…) | Subclass `FileWriter`; the upstream classes don’t care |

---

## 🛠️ Tech stack

- **[pandas](https://pandas.pydata.org/)** — tabular data, Excel I/O, the backbone of every class.
- **[NumPy](https://numpy.org/)** — the Euclidean distance math.
- **[openpyxl](https://openpyxl.readthedocs.io/)** — under the hood, `pandas.to_excel`.
- **Python 3.10+** — `str | None` annotations and modern f-strings.

There are no heavyweight dependencies. The whole pipeline runs in a stock scientific-Python environment.

---

## 🤝 Contributing

Pull requests are welcome. For substantial changes, please open an issue first to discuss what you’d like to change. Keep new code in the same single-responsibility-per-class style — that is the whole point of this rewrite.

---

## 📚 Context & related work

- The **downstream model** (LSTM-based drought predictor) lives in a sibling repository: [`A-Infor/Python-OOP-LSTM-Drought-Predictor`](https://github.com/A-Infor/Python-OOP-LSTM-Drought-Predictor) (more general) / [`JVSREco19/RedeNeuralSecas`](https://github.com/JVSREco19/RedeNeuralSecas) (more specific).
- The SPEI (Standardized Precipitation-Evapotranspiration Index) methodology was developed by Vicente-Serrano, Beguería & López-Moreno (2010).
- IBGE municipal geocodes follow the [7-digit official table](https://www.ibge.gov.br/).

---

## 📚 Citation & context

If you use this project in academic work, please reference the original dissertation it was built for. 

---

## 📄 License

No `LICENSE` file is currently present in this repository. Until one is added, the project's copyright status is unspecified and the **default rules of your jurisdiction apply** (in most countries, that means *all rights reserved* by the author).

If you intend to use, modify, or redistribute this code, please contact the author to clarify the intended terms.
