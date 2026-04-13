# -*- coding: utf-8 -*-
"""
Tests unitaires pour meteofrtoepw.solar

Principalement rédigé avec Claude, à vérifier
"""

import math
import pytest
from meteofrtoepw.solar import (
    DAY, day_angle, solar_declination, solar_elevation, Ct, I0
)


class TestDAY:
    def test_premier_janvier(self):
        assert DAY(1, 1) == 1

    def test_premier_fevrier(self):
        assert DAY(1, 2) == 32

    def test_solstice_ete(self):
        # 21 juin = jour 172
        assert DAY(21, 6) == 172

    def test_31_decembre(self):
        assert DAY(31, 12) == 365


class TestSolarDeclination:
    def test_equinoxe_printemps(self):
        # Aux équinoxes (~20 mars, jour 79), déclinaison ≈ 0°
        assert abs(solar_declination(79)) < 2.0

    def test_solstice_ete(self):
        # Solstice d'été (~21 juin, jour 172), déclinaison ≈ +23.45°
        assert abs(solar_declination(172) - 23.45) < 1.0

    def test_solstice_hiver(self):
        # Solstice d'hiver (~21 déc, jour 355), déclinaison ≈ -23.45°
        assert abs(solar_declination(355) + 23.45) < 1.0


class TestSolarElevation:
    def test_nuit_negatif_clampe(self):
        # À minuit, la hauteur solaire doit être 0 (clampée)
        assert solar_elevation(0, 172, 1, 48.8) == 0.0

    def test_midi_ete_positif(self):
        # À midi en été à Paris, hauteur > 0
        assert solar_elevation(12, 172, 1, 48.8) > 0.0

    def test_valeur_max_raisonnable(self):
        # La hauteur solaire maximale ne peut pas dépasser 90°
        assert solar_elevation(12, 172, 1, 48.8) <= 90.0


class TestI0:
    def test_nuit_zero(self):
        # Pas de rayonnement extraterrestre la nuit
        assert I0(0, 172, 1, 48.8) == 0.0

    def test_jour_positif(self):
        # Rayonnement positif en journée en été
        assert I0(12, 172, 1, 48.8) > 0.0

    def test_valeur_max(self):
        # I0 ne peut pas dépasser Isc * facteur d'excentricité (~1400 W/m²)
        assert I0(12, 172, 1, 0.0) < 1450.0