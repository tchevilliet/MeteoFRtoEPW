# -*- coding: utf-8 -*-
"""
Fonctions de géométrie solaire.

Les équations proviennent principalement de Lanini, Fabienne, 2010. 
Division of global radiation into direct radiation and diffuse radiation 
(Master’s thesis). Faculty of Science, University of Bern, Bern.

Les formules ne sont pour l'instant pas ajustées pour les années bissextiles.

Citant : 
  - Cooper, P. I. (1969). Solar Energy, 12(3), 333-346.
  - Iqbal, M. (1983). An Introduction to Solar Radiation. Academic Press.
  - El Mghouchi et al. (2016). Renewable and Sustainable Energy Reviews, 56, 87-99.
  - Spencer, J.W. (1971). Search, 2(5):172.

@author: thibault.chevilliet
"""

import math

def is_leap(y: int) -> bool:
    return (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)

def DAY(day: int, month: int, year : int = None) -> int:
    """
    Retourne le numéro du jour dans l'année (1–365).
    Les années bissextiles ne sont pas encore gérées.

    Parameters
    ----------
    day : int
        Jour du mois, entre 1 et 31.
    month : int
        Mois, entre 1 et 12.
    year : int, optional
        Année. Si None, pas d'année bissextile possible

    Returns
    -------
    int
        Numéro du jour entre 1 et 365 (ou 366 si année bissextile).
    """


    durations = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
                 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
    return sum(durations[k] for k in durations if k < month) + day


def day_angle(day: int) -> float:
    """
    Angle journalier en radians selon Iqbal (1983).

    Parameters
    ----------
    day : int
        Numéro du jour entre 1 et 365.

    Returns
    -------
    float
        Angle journalier en radians.
    """
    return 2 * math.pi * (day - 1) / 365.2425


def solar_declination(day: int) -> float:
    """
    Déclinaison solaire en degrés selon Cooper (1969).

    Parameters
    ----------
    day : int
        Numéro du jour entre 0 et 365.

    Returns
    -------
    float
        Déclinaison solaire en degrés.
    """
    return 23.45 * math.sin((day + 284) * 2 * math.pi / 365)


def eq_of_time(day: int) -> float:
    """
    Équation du temps en heures selon Iqbal (1983).

    Parameters
    ----------
    day : int
        Numéro du jour entre 1 et 365.

    Returns
    -------
    float
        Équation du temps en minutes.
    """
    GAMMA = day_angle(day)
    return 229.18 * (
        0.000075
        + 0.01868 * math.cos(GAMMA)
        - 0.032077 * math.sin(GAMMA)
        - 0.014615 * math.cos(2 * GAMMA)
        - 0.04089 * math.sin(2 * GAMMA)
    ) / 60


def apparent_solar_time(hour: int, day: int, time_zone: int, longitude: float) -> float:
    """
    Temps solaire apparent selon Iqbal (1983).

    Parameters
    ----------
    hour : int
        Heure de la journée entre 0 et 23.
    day : int
        Numéro du jour entre 1 et 365.
    time_zone : int
        Fuseau horaire en heures (−12 à +12).
    longitude : float
        Longitude en degrés.

    Returns
    -------
    float
        Temps solaire apparent.
    """
    Lst = 15 * ((longitude / 15) + longitude * 0.5 / abs(longitude))
    Lcorr = 4 * (longitude - Lst)
    Et = eq_of_time(day)
    return hour + Lcorr + Et


def solar_elevation(hour: int, day: int, time_zone: int, latitude: float) -> float:
    """
    Hauteur solaire estimée en degrés (≥ 0) selon El Mghouchi et al. (2016).

    Parameters
    ----------
    hour : int
        Heure de la journée entre 0 et 23.
    day : int
        Numéro du jour entre 0 et 365.
    time_zone : int
        Fuseau horaire en heures.
    latitude : float
        Latitude en degrés (−90 à +90).

    Returns
    -------
    float
        Hauteur solaire en degrés, clampée à 0 si négatif.
    """
    # Temps solaire simplifié (sans correction de longitude)
    solar_t = hour - time_zone if hour >= time_zone else hour - time_zone + 24
    delta = math.radians(solar_declination(day))
    cosT = math.cos(math.radians(15 * (solar_t - 12)))
    phi = math.radians(latitude)
    h = math.asin(cosT * math.cos(delta) * math.cos(phi)
                  + math.sin(delta) * math.sin(phi)) * 180 / math.pi
    return max(h, 0.0)


def Ct(day: int) -> float:
    """
    Facteur de correction d'excentricité selon Spencer (1971).

    Parameters
    ----------
    day : int
        Numéro du jour entre 1 et 365.

    Returns
    -------
    float
        Facteur de correction (sans dimension).
    """
    GAMMA = day_angle(day)
    return (
        1.00011
        + 0.034221 * math.cos(GAMMA)
        + 0.00128 * math.sin(GAMMA)
        + 0.000719 * math.cos(2 * GAMMA)
        + 0.000077 * math.sin(2 * GAMMA)
    )


def I0(hour: int, day: int, time_zone: int, latitude: float, Isc: float = 1366.1) -> float:
    """
    Rayonnement extraterrestre sur plan horizontal corrigé selon Oke (1978).

    Parameters
    ----------
    hour : int
        Heure entre 0 et 23.
    day : int
        Numéro du jour entre 1 et 365.
    time_zone : int
        Fuseau horaire.
    latitude : float
        Latitude en degrés.
    Isc : float, optional
        Constante solaire en W/m². Défaut : 1366.1 (Frohlich, 2006).

    Returns
    -------
    float
        Rayonnement extraterrestre sur plan horizontal (W/m²).
    """
    h = solar_elevation(hour, day, time_zone, latitude)
    return Ct(day) * Isc * math.sin(math.radians(h))