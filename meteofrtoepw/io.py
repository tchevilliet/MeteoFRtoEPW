# -*- coding: utf-8 -*-
"""
Lecture des fichiers CSV Météo-France et conversion au format EPW.

Source des données : https://meteo.data.gouv.fr/
Format EPW : https://climate.onebuilding.org/papers/EnergyPlus_Weather_File_Format.pdf

@author: thibault.chevilliet
"""

from numpy import int_
import pandas as pd
from ladybug.epw import EPW
from ladybug.location import Location

from .solar import DAY, is_leap
from .brl import D_BRL


# Colonnes attendues dans le fichier EPW de sortie
# (les champs marqués "not currently used" dans la spec EnergyPlus sont omis,
#  sauf le rayonnement global qui est présent dans la source CSV)
OUTPUT_COLUMNS = [
    'year', 'month', 'day', 'hour',
    'dry_bulb_temperature',
    'dew_point_temperature',
    'relative_humidity',
    'atmospheric_station_pressure',
    # 'horizontal_infrared_radiation_intensity',  # non utilisé
    # 'global_horizontal_radiation',              # intermédiaire de calcul
    'direct_normal_radiation',
    'diffuse_horizontal_radiation',
    'wind_direction',
    'wind_speed',
    'total_sky_cover',
    'opaque_sky_cover',
    # 'present_weather_observation',  # non utilisé
    # 'present_weather_codes',        # non utilisé
    # 'snow_depth',                   # non utilisé
    # 'liquid_precipitation_depth',   # non utilisé
]

# Correspondance entre les en-têtes CSV source et les noms EPW,
# avec le facteur de conversion associé.
# Format : { 'code_csv': ('nom_epw', facteur) }
HEADER_TRANSLATE = {
    'T':    ('dry_bulb_temperature',         1.0),
    'TD':   ('dew_point_temperature',        1.0),
    'U':    ('relative_humidity',            1.0),
    'PSTAT':('atmospheric_station_pressure', 100),    # hPa → Pa
    'GLO':  ('global_horizontal_radiation',  10000 / 3600),  # J/cm² → Wh/m²
    'DD':   ('wind_direction',               1.0),
    'FF':   ('wind_speed',                   1.0),
    'N':    ('total_sky_cover',              1.25),   # octas → dixièmes
    'DIR':  ('direct_normal_radiation',      10000 / 3600),  # J/cm² → Wh/m²
    'DIF':  ('diffuse_horizontal_radiation', 10000 / 3600),  # J/cm² → Wh/m²
    'NBAS': ('Nl',                           1.25),   # octas → dixièmes
    'N1':   ('Nm',                           1.25),
    'N2':   ('Nh',                           1.25),   # N3 négligé
}


class StationWeather:
    """
    Représente les données météorologiques d'une station Météo-France
    et fournit les outils pour les convertir au format EPW.

    Attributes
    ----------
    name : str
        Nom de la localité (utilisé dans le fichier EPW).
    station : str
        Identifiant de la station Météo-France.
    period : tuple
        Période couverte par les données (date_début, date_fin).
    latitude : float
        Latitude de la station en degrés.
    longitude : float
        Longitude de la station en degrés.
    altitude : float
        Altitude de la station en mètres.
    data : pd.DataFrame
        Données brutes importées et converties.
    epw : EPW
        Objet EPW Ladybug une fois `to_epw()` appelé.
    translator : dict
        Table de correspondance CSV → EPW (par défaut : HEADER_TRANSLATE).
    time_zone : int
        Fuseau horaire UTC.
    """

    def __init__(
        self,
        name: str = None,
        station: str = None,
        period: tuple = (None, None),
        latitude: float = None,
        longitude: float = None,
        altitude: float = None,
        data: pd.DataFrame = None,
        epw: EPW = None,
        translator: dict = None,
        time_zone: int = None,
        year : int = None,
        station_id : int = 0
    ):
        self.name = name
        self.station = station
        self.period = period
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.data = data
        self.epw = epw
        self.translator = translator if translator is not None else HEADER_TRANSLATE
        self.time_zone = time_zone
        self.year = year
        self.station_id = int(station_id)

        # DataFrame de sortie (colonnes EPW)
        self.output_df = pd.DataFrame(columns=OUTPUT_COLUMNS)

    # ------------------------------------------------------------------
    # Import et préparation des données
    # ------------------------------------------------------------------

    def import_source(self, path: str, station_name: str) -> None:
        """
        Importe un fichier CSV Météo-France, filtre par station et
        applique les conversions d'unités.

        Parameters
        ----------
        path : str
            Chemin vers le fichier CSV source.
        station_name : str
            Valeur du champ NOM_USUEL à sélectionner.
        """
        df = pd.read_csv(path, sep=';')
        
        # Décodage de la colonne de date AAAAMMJJHH
        df['year']  = df['AAAAMMJJHH'].astype(str).str[:4].astype(int)
        df['month'] = df['AAAAMMJJHH'].astype(str).str[4:6].astype(int)
        df['day']   = df['AAAAMMJJHH'].astype(str).str[6:8].astype(int)
        df['hour']  = df['AAAAMMJJHH'].astype(str).str[8:10].astype(int)
        df.drop(columns=['AAAAMMJJHH'], inplace=True)

        self.data = df[df['NOM_USUEL'] == station_name].copy()
        self.data.reset_index(drop=True, inplace=True)

        # Conversion des colonnes source
        for k, (col_name, factor) in self.translator.items():
            if k in self.data.columns:
                # TODO : envisager une stratégie d'interpolation plutôt que fillna(0)
                self.data[k] = self.data[k].fillna(0) * factor
                self.data.rename(columns={k: col_name}, inplace=True)

    def localize(self, time_zone: int) -> None:
        """
        Renseigne les métadonnées géographiques à partir des données importées.

        Parameters
        ----------
        time_zone : int
            Fuseau horaire UTC (ex. : 1 pour la France en hiver).

        Raises
        ------
        TypeError
            Si `import_source` n'a pas encore été appelé.
        """
        if self.data is None:
            raise TypeError("Aucune donnée disponible. Appelez d'abord import_source().")
        self.latitude  = float(self.data['LAT'].iloc[0])
        self.longitude = float(self.data['LON'].iloc[0])
        self.altitude  = float(self.data['ALTI'].iloc[0])
        
        self.station_id  = int(self.data['NUM_POSTE'].iloc[0])
        self.time_zone = time_zone

    def time_slicer(self, year: int) -> None:
        """
        Filtre les données pour ne conserver qu'une seule année.

        Parameters
        ----------
        year : int
            Année à conserver.
        """
        self.data = self.data[self.data['year'] == year].copy()
        self.data.reset_index(drop=True, inplace=True)
        self.year = year

    # ------------------------------------------------------------------
    # Traitement des données
    # ------------------------------------------------------------------

    def gap_fill(self) -> None:
        """
        Complète les données manquantes et calcule les rayonnements diffus
        et direct via le modèle BRL.

        - La couverture nuageuse opaque est assimilée à la couverture totale.
        - Le rayonnement diffus est estimé via D_BRL.
        - Le rayonnement direct normal = rayonnement global − diffus.
        """
        # Couverture opaque ≈ couverture totale (cohérent avec les fichiers EPW existants)
        self.data['opaque_sky_cover'] = self.data['total_sky_cover']

        # Numéro de jour dans l'année (1–365)
        self.data['DAY'] = self.data.apply(
            lambda row: DAY(row['day'], row['month'],row['year']), axis=1
        )

        # Calcul diffus / direct via BRL pour chaque heure
        diffuse_values = []
        direct_values  = []

        for i in self.data.index:
            day_num = self.data.at[i, 'DAY']
            hour    = self.data.at[i, 'hour']

            # Liste du rayonnement global pour le jour courant (avec sentinelles 0)
            daily_glob = list(
                self.data['global_horizontal_radiation'][self.data['DAY'] == day_num]
            )
            list_glob_rad = [0] + daily_glob + [0]

            diffuse = D_BRL(
                list_glob_rad, hour, day_num,
                self.time_zone, self.latitude, self.longitude,
            )
            direct = self.data.at[i, 'global_horizontal_radiation'] - diffuse

            diffuse_values.append(diffuse)
            direct_values.append(max(direct, 0.0))  # évite les valeurs négatives

        self.data['diffuse_horizontal_radiation'] = diffuse_values
        self.data['direct_normal_radiation']      = direct_values

    def wmo_code_to_epw_code(self, path_to_table: str) -> None:
        """
        Convertit les codes météo WMO présents dans `data` en codes EPW.

        Parameters
        ----------
        path_to_table : str
            Chemin vers un CSV de correspondance WMO → EPW avec les colonnes :
            WW, Present Weather Observation, Present Weather Codes.
        """
        converter = pd.read_csv(
            path_to_table,
            sep=',',
            dtype={
                'WW': int,
                'Present Weather Observation': int,
                'Present Weather Codes': str,
            },
        ).set_index('WW')

        for i in self.data.index:
            wmo = self.data.at[i, 'WW']
            self.data.at[i, 'Present Weather Observation'] = \
                converter.at[wmo, 'Present Weather Observation']
            self.data.at[i, 'Present Weather Codes'] = \
                converter.at[wmo, 'Present Weather Codes']

    # ------------------------------------------------------------------
    # Export EPW
    # ------------------------------------------------------------------

    def to_epw(self, path: str) -> None:
        """
        Génère et écrit le fichier EPW.

        Parameters
        ----------
        path : str
            Chemin de destination du fichier `.epw`.

        Raises
        ------
        ValueError
            Si des champs obligatoires sont absents de `data`.
        """
        required_fields = [
            'dry_bulb_temperature', 'dew_point_temperature',
            'relative_humidity', 'atmospheric_station_pressure',
            'direct_normal_radiation', 'diffuse_horizontal_radiation',
            'wind_direction', 'wind_speed',
            'total_sky_cover', 'opaque_sky_cover',
        ]

        missing = [f for f in required_fields if f not in self.data.columns]
        if missing:
            raise ValueError(
                f"Champs manquants dans les données : {missing}. "
                "Vérifiez que import_source() et gap_fill() ont été appelés."
            )
        


        self.epw = EPW.from_missing_values(
            is_leap_year =is_leap(self.year)
            )
        self.epw.location = Location(
            city=self.name or 'Unknown',
            state = ' ',
            country='France',            
            latitude=self.latitude,
            longitude=self.longitude,
            elevation=self.altitude,
            time_zone=self.time_zone,
            station_id = self.station_id,
            source = "MeteoFR"
        )
        getattr(self.epw, "years").values = list(self.data["year"])

        for field in required_fields:
            getattr(self.epw, field).values = list(self.data[field])

        self.epw.write(path)