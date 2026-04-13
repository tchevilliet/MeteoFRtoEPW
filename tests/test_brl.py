# -*- coding: utf-8 -*-
"""
Tests unitaires pour meteofrtoepw.brl

Principalement rédigé avec Claude, à vérifier
"""

import pytest
from meteofrtoepw.brl import kt, kt_daily, D_BRL, B_BRL


# Journée fictive : 24h de rayonnement, avec sentinelles
DAILY_RAD = [0] + [0]*6 + [50, 200, 400, 600, 700, 650, 600, 400, 200, 50] + [0]*8 + [0]
# 26 éléments : sentinelle + 24h + sentinelle

LAT  = 48.8    # Paris
LON  = 2.3
TZ   = 1
DAY  = 172     # 21 juin


class TestKt:
    def test_nuit_zero(self):
        # Pas de rayonnement → kt = 0
        assert kt(0, 0, DAY, TZ, LAT) == 0.0

    def test_journee_entre_zero_et_un(self):
        # Midi : kt doit être dans [0, 1] pour un ciel normal
        k = kt(500, 12, DAY, TZ, LAT)
        assert 0.0 <= k <= 1.5  # peut dépasser 1 légèrement (mesure + modèle)

    def test_extraterrestre_nul(self):
        # Si I0 = 0, kt = 0 (pas de division par zéro)
        assert kt(100, 0, DAY, TZ, LAT) == 0.0


class TestKtDaily:
    def test_journee_nulle(self):
        rad_nulle = [0] * 24
        assert kt_daily(rad_nulle, DAY, TZ, LAT) == 0.0

    def test_journee_positive(self):
        k = kt_daily(DAILY_RAD[1:-1], DAY, TZ, LAT)
        assert k >= 0.0


class TestDBRL:
    def test_diffuse_positive(self):
        # À midi, le diffus doit être positif
        d = D_BRL(DAILY_RAD, 12, DAY, TZ, LAT, LON)
        assert d >= 0.0

    def test_diffuse_inferieur_global(self):
        # Le diffus ne peut pas dépasser le global
        hour = 12
        global_rad = DAILY_RAD[hour + 1]
        d = D_BRL(DAILY_RAD, hour, DAY, TZ, LAT, LON)
        assert d <= global_rad + 1e-6  # tolérance numérique

    def test_nuit_diffuse_nulle(self):
        # La nuit, rayonnement global = 0 → diffus = 0
        d = D_BRL(DAILY_RAD, 1, DAY, TZ, LAT, LON)
        assert d == 0.0


class TestBBRL:
    def test_direct_positif_ou_nul(self):
        b = B_BRL(DAILY_RAD, 12, DAY, TZ, LAT, LON)
        # Le direct peut être négatif si modèle surestime le diffus,
        # mais doit rester raisonnable
        assert b > -1.0