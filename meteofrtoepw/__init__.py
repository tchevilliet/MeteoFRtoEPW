#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
meteofrtoepw
============
Conversion de données météo françaises (Météo-France / data.gouv.fr)
au format EPW (EnergyPlus Weather) pour la simulation thermique du bâtiment.

Modules
-------
io      : Lecture CSV et classe StationWeather
solar   : Fonctions de géométrie solaire
brl     : Modèle BRL de décomposition du rayonnement global

Usage rapide
------------
>>> from meteofrtoepw.io import StationWeather
>>> sw = StationWeather(name="Paris-Montsouris")
>>> sw.import_source("meteo_data.csv", "PARIS-MONTSOURIS")
>>> sw.localize(time_zone=1)
>>> sw.time_slicer(2023)
>>> sw.gap_fill()
>>> sw.to_epw("paris_2023.epw")
"""

__version__ = "1.0.0"
__author__ = "Thibault Chevilliet"

from . import io, solar, brl
from .io import StationWeather

__all__ = ["StationWeather", "io", "solar", "brl"]