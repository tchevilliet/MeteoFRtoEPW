# -*- coding: utf-8 -*-
"""
Modèle BRL de décomposition du rayonnement solaire global en composantes
directe et diffuse.

Référence principale :
    Ridley, B., Boland, J., & Lauret, P. (2010).
    Modelling of diffuse solar fraction with multiple predictors.
    Renewable Energy, 35, 478–483.
    doi: 10.1016/j.renene.2009.07.018

@author: thibault.chevilliet
"""

import numpy as np
from .solar import I0, apparent_solar_time, solar_elevation


def kt(G_measured: float, hour: int, day: int,
       time_zone: int, latitude: float, Isc: float = 1366.1) -> float:
    """
    Indice de clarté horaire (clearness index) selon Liu & Jordan (1960).

    Parameters
    ----------
    G_measured : float
        Rayonnement global horizontal mesuré (W/m²).
    hour : int
        Heure entre 0 et 23.
    day : int
        Numéro du jour entre 1 et 365.
    time_zone : int
        Fuseau horaire.
    latitude : float
        Latitude en degrés.
    Isc : float, optional
        Constante solaire en W/m². Défaut : 1366.1.

    Returns
    -------
    float
        Indice de clarté (sans dimension).
    """
    Gextra = I0(hour, day, time_zone, latitude, Isc)
    if Gextra == 0:
        return 0.0
    return G_measured / Gextra


def kt_daily(list_I: list, day: int, time_zone: int, latitude: float,
             Isc: float = 1366.1) -> float:
    """
    Indice de clarté journalier selon Ridley et al. (2010).

    Parameters
    ----------
    list_I : list of float
        Rayonnements globaux horaires sur la journée (24 valeurs).
    day : int
        Numéro du jour entre 1 et 365.
    time_zone : int
        Fuseau horaire.
    latitude : float
        Latitude en degrés.
    Isc : float, optional
        Constante solaire en W/m². Défaut : 1366.1.

    Returns
    -------
    float
        Indice de clarté journalier (sans dimension).
    """
    l_io = [I0(h, day, time_zone, latitude, Isc) for h in range(24)]
    total_io = sum(l_io)
    if total_io == 0:
        return 0.0
    return sum(list_I) / total_io


def persistence_factor(G: float, G_plus1: float, G_minus1: float,
                       hour: int, day: int, time_zone: int,
                       latitude: float, Isc: float = 1366.1) -> float:
    """
    Facteur de persistance selon Ridley et al. (2010).

    Parameters
    ----------
    G : float
        Rayonnement global à l'heure h (W/m²).
    G_plus1 : float
        Rayonnement global à h+1 (W/m²).
    G_minus1 : float
        Rayonnement global à h-1 (W/m²).
    hour : int
        Heure entre 0 et 23.
    day : int
        Numéro du jour entre 1 et 365.
    time_zone : int
        Fuseau horaire.
    latitude : float
        Latitude en degrés.
    Isc : float, optional
        Constante solaire en W/m². Défaut : 1366.1.

    Returns
    -------
    float
        Facteur de persistance (sans dimension).
    """
    k = kt(G, hour, day, time_zone, latitude, Isc)
    k_plus1 = kt(G_plus1, hour + 1, day, time_zone, latitude, Isc)
    k_minus1 = kt(G_minus1, hour - 1, day, time_zone, latitude, Isc)

    if k == 0 and k_plus1 > 0:
        return k_plus1
    elif k == 0 and k_minus1 > 0:
        return k_minus1
    else:
        return (k_plus1 + k_minus1) / 2


def D_BRL(list_I: list, hour: int, day: int,
          time_zone: int, latitude: float, longitude: float,
          Isc: float = 1366.1) -> float:
    """
    Rayonnement diffus horizontal estimé par le modèle BRL (Ridley et al., 2010).

    Parameters
    ----------
    list_I : list of float
        Rayonnements globaux horaires sur la journée, avec deux sentinelles :
        [0] + 24 valeurs + [0] (soit 26 éléments au total).
        Cette convention évite les IndexError en début/fin de journée.
    hour : int
        Heure entre 0 et 23 (index dans list_I décalé de 1 à cause de la sentinelle).
    day : int
        Numéro du jour entre 1 et 365.
    time_zone : int
        Fuseau horaire.
    latitude : float
        Latitude en degrés.
    longitude : float
        Longitude en degrés.
    Isc : float, optional
        Constante solaire en W/m². Défaut : 1366.1.

    Returns
    -------
    float
        Rayonnement diffus horizontal modélisé (W/m²).

    Notes
    -----
    list_I doit avoir la forme [0] + valeurs_journée + [0].
    L'heure h correspond à list_I[h+1].
    """
    # Avec la sentinelle, l'indice courant est hour+1
    idx = hour + 1
    G_now = list_I[idx]
    G_prev = list_I[idx - 1]
    G_next = list_I[idx + 1]

    k = kt(G_now, hour, day, time_zone, latitude, Isc)
    As = apparent_solar_time(hour, day, time_zone, longitude)
    phi = solar_elevation(hour, day, time_zone, latitude)
    k_d = kt_daily(list_I[1:-1], day, time_zone, latitude, Isc)
    psi = persistence_factor(G_now, G_next, G_prev, hour, day, time_zone, latitude, Isc)

    a = -5.32 + 7.28 * k - 0.03 * As - 0.0047 * phi + 1.72 * k_d + 1.08 * psi
    diffuse_fraction = 1 / (1 + np.exp(a))
    return G_now * diffuse_fraction


def B_BRL(list_I: list, hour: int, day: int,
          time_zone: int, latitude: float, longitude: float,
          Isc: float = 1366.1) -> float:
    """
    Rayonnement direct horizontal estimé (= global - diffus).

    Parameters
    ----------
    Voir D_BRL pour la description des paramètres.

    Returns
    -------
    float
        Rayonnement direct horizontal modélisé (W/m²).
    """
    return list_I[hour + 1] - D_BRL(list_I, hour, day, time_zone, latitude, longitude, Isc)