# Read me file
Test.

# MeteoFRtoEPW

Conversion de données météorologiques françaises (Météo-France / data.gouv.fr) au format **EPW** (EnergyPlus Weather) pour la simulation thermique du bâtiment.

## Fonctionnalités

- Import des fichiers CSV horaires de Météo-France (`data.gouv.fr`)
- Conversion des unités (hPa → kPa, J/cm² → Wh/m², octas → dixièmes…)
- Décomposition du rayonnement global en rayonnement **diffus** et **direct** via le modèle **BRL** (Ridley, Boland & Lauret, 2010)
- Export au format `.epw` compatible EnergyPlus, Ladybug Tools, OpenStudio…

## Installation

```bash
git clone https://github.com/tchevilliet/MeteoFRtoEPW.git
cd MeteoFRtoEPW
pip install .
```

**Dépendances :** `pandas`, `numpy`, `ladybug-core`

## Utilisation rapide

```python
from meteofrtoepw.io import StationWeather

sw = StationWeather(name="Paris-Montsouris")

# 1. Importer les données CSV Météo-France
sw.import_source("meteo_data.csv", station_name="PARIS-MONTSOURIS")

# 2. Renseigner les métadonnées géographiques (fuseau horaire UTC)
sw.localize(time_zone=1)

# 3. Filtrer sur une année
sw.time_slicer(2023)

# 4. Calculer diffus / direct (modèle BRL)
sw.gap_fill()

# 5. Exporter en EPW
sw.to_epw("paris_montsouris_2023.epw")
```

## Données source

Les fichiers CSV sont disponibles sur [data.gouv.fr](https://meteo.data.gouv.fr/). Télécharger les données horaires (`RR-T-Vent`) pour la station souhaitée.

## Structure du projet

```
meteofrtoepw/
├── __init__.py     ← Point d'entrée du package
├── io.py           ← Import CSV + classe StationWeather + export EPW
├── solar.py        ← Fonctions de géométrie solaire
└── brl.py          ← Modèle BRL (décomposition diffus/direct)
tests/
├── test_solar.py
└── test_brl.py
tutorials/          ← Notebooks d'exemple
pyproject.toml
```

## Lancer les tests

```bash
pip install pytest
pytest tests/
```

## Références
- Lanini, F. (2010) Division of global radiation into direct radiation and diffuse radiation (Master’s thesis). Faculty of Science, University of Bern, Bern.
- Ridley, B., Boland, J., & Lauret, P. (2010). *Modelling of diffuse solar fraction with multiple predictors.* Renewable Energy, 35, 478–483.
- Iqbal, M. (1983). *An Introduction to Solar Radiation.* Academic Press.
- Cooper, P. I. (1969). *The absorption of radiation in solar stills.* Solar Energy, 12(3), 333–346.
- [EnergyPlus Weather File Format](https://climate.onebuilding.org/papers/EnergyPlus_Weather_File_Format.pdf)

## Licence

MIT — Thibault Chevilliet, ENPC