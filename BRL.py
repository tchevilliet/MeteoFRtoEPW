#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  6 15:47:52 2025

@author: thibault.chevilliet

The equations come mainly from
Lanini, Fabienne, 2010. 
Division of global radiation into direct radiation and diffuse radiation 
(Master’s thesis). Faculty of Science, University of Bern, Bern.

"""

import math
import numpy as np

def DAY(day,month):
    """
    Return the day of the year between 1 and 365. Leap year not considered yet. 

    Parameters
    ----------
    day : int
        day of the month between 1 and 31.
    month : int
        month between 1 and 12.

    Returns
    -------
    res : int
        Day number betwwen 1 and 365.

    """
    durations = {1 : 31 , 2: 28 , 3 : 31, 4 : 30, 5 : 31, 6 : 30, 7 : 31, 8 : 31, 9 : 30,
     10 : 31 , 11 : 30, 12 : 31}
    
    res = sum([durations[k] for k in durations.keys() if k<month])+day
    
    return res

def solar_time(hour,time_zone) :
    """
    Returns the Solar time, ignoring longitude correction 

    Parameters
    ----------
    hour : int
        between 0 and 23.
    time_zone : int
        Time zone in hours between -12 and +12.

    Returns
    -------
    int
        Solar time between 0 and 23.

    """
    if hour >= time_zone :
        res = hour-time_zone
    else :
        res = hour-time_zone + 24
    return res

def solar_declination(day) :
    """
    returns the estimated solar declination according to Cooper, P. I. (1969). 
    The absorption of radiation in solar stills. Solar energy, 12(3), 333-346.
    
    Parameters
    ----------
    day : int
        between 0 and 365

    Returns
    -------
    float
        Estimated solar declination in degrees.

    """
    # return -23.45*math.cos(math.radians(360*(day+10)/365.25))
    return (23.45*math.sin((day+284)*2*math.pi/365))


# import matplotlib.pyplot as plt
# fig,ax = plt.subplots()
# ax.plot(range(1,365),[solar_declination(d) for d in range(1,365)])
# plt.show()

def solar_elevation(hour,day,time_zone,latitude):
    """
    Returns the estimated solar elevation according to El Mghouchi, Y., 
    El Bouardi, A., Choulli, Z., & Ajzoul, T. (2016). Models for obtaining 
    the daily direct, diffuse and global solar radiations. 
    Renewable and Sustainable Energy Reviews, 56, 87-99.
    
    Parameters
    ----------
    solar_time : int
        true solar time.
    day : int
        between 0 and 365.
    latitude : float
        Latitude in degrees. Between -90° and 90°

    Returns
    -------
    float
        Estimated solar elevation in degrees.

    """
    delta = math.radians(solar_declination(day))
    cosT = math.cos(math.radians(15*(solar_time(hour,time_zone)-12)))
    cosdelta , sindelta = math.cos(delta), math.sin(delta)
    phi = math.radians(latitude)
    cosphi , sinphi = math.cos(phi), math.sin(phi)
    h = math.asin(cosT*cosdelta*cosphi+sindelta*sinphi)*180/math.pi
    if h>=0 :
        res=h  
    else : 
        res=0
    return res

def day_angle(day) :
    """
    Return the day angle in radians according to 
    M. Iqbal. An introduction to solar radiation. Academic Press, 1983

    Parameters
    ----------
    day : int
        day number between 1 and 365.

    Returns
    -------
    float
        day angle in radians.

    """
    return 2*math.pi*(day-1)/365.2425

def eq_of_time(day) :
    """
    Return the "equation of time" in hours according to 
    M. Iqbal. An introduction to solar radiation. Academic Press, 1983

    Parameters
    ----------
    day : int
        day number between 1 and 365.

    Returns
    -------
    float
        Equation of time in minutes.

    """
    GAMMA = day_angle(day)
    return 229.18*(0.000075 + 0.01868*math.cos(GAMMA)-0.032077*math.sin(GAMMA)-0.014615*math.cos(2*GAMMA)-0.04089*math.sin(2*GAMMA))/60
    
def apparent_solar_time(hour ,day, time_zone, longitude) :
    """
    Return Apparent solar time according to 
    M. Iqbal. An introduction to solar radiation. Academic Press, 1983

    Parameters
    ----------
    hour : int
        hour of the day between 0 and 23.
    day : int
        day number between 1 and 365.
    time_zone : int
        Time zone in hours between -12 and +12.
    longitude : float
        Longitude in degrees.

    Returns
    -------
    float
        Apparent or true solar time.

    """
    Lst = 15*((longitude/15)+longitude*0.5/abs(longitude))
    Lcorr = 4*(longitude-Lst)
    Et = eq_of_time(day)
    return hour+Lcorr+Et

def hour_angle(hour ,day, time_zone, longitude) :
    return 15*(12-apparent_solar_time(hour, day, time_zone, longitude))

def Ct(day) :
    """
    Eccentricity correction factor according to 
    J.W. Spencer. 
    Fourier series representation of the position of the sun. 
    Search, 2(5):172, 1971

    Parameters
    ----------
    day : int
        day number between 1 and 365.

    Returns
    -------
    float
        Eccentricity correction factor, dimensionless.

    """
    GAMMA = day_angle(day)
    cosgam,singam = math.cos(GAMMA),math.sin(GAMMA)
    cos2gam,sin2gam = math.cos(2*GAMMA),math.sin(2*GAMMA)
    return 1.00011 + 0.034221*cosgam + 0.00128*singam + 0.000719*cos2gam + 0.000077*sin2gam

def I0 (hour, day, time_zone, latitude,Isc=1366.1) :
    """
    Corrected extraterrestrial radiation according to 
    T.R. Oke. Boundary Layer Climates. Routledge, 1978.
    
    Parameters
    ----------
    hour : int
        hour of the day between 0 and 23.
    day : int
        day number between 1 and 365.
    time_zone : int
        Time zone in hours between -12 and +12.
    longitude : float
        Longitude in degrees.
    Isc : float, optional
        Total solar irradiance. The default is 1366.1 W/m2 according to 
        C. Frohlich. Solar irradiance variability since 1978. 
        Space Science Reviews, 25(23):43774380, 2006.

    Returns
    -------
    float
        extraterrestrial radiation on horizontal plane.

    """
    E0= Ct(day)
    h=solar_elevation(hour, day, time_zone, latitude)
    sinh = math.sin(math.radians(h))
    return E0*Isc*sinh

def kt(G_measured,hour, day, time_zone, latitude,Isc=1366.1) :
    """
    Returns Clearness index according to 
    B.Y.H. Liu and R.C. Jordan. The interralationship and characteristic 
    distribution of direct, diffuse and total solar radiation. 
    Solar Energy, 4:1–9, 1960

    Parameters
    ----------
    G_measured : float
        Measured global radiations on horizontal plane (W/m2).
    hour : int
        hour of the day between 0 and 23.
    day : int
        day number between 1 and 365.
    time_zone : int
        Time zone in hours between -12 and +12.
    longitude : float
        Longitude in degrees.
    Isc : float, optional
        Total solar irradiance. The default is 1366.1 W/m2 according to 
        C. Frohlich. Solar irradiance variability since 1978. 
        Space Science Reviews, 25(23):43774380, 2006.
    Returns
    -------
    res : float
        Clearness index (dimensionless).

    """
    
    Gextra = I0(hour, day, time_zone, latitude, Isc)
    if Gextra == 0 :
        res = 0
    else :
        res = G_measured/Gextra
    return res

def kt_daily(list_I,day, time_zone, latitude):
    """
    Returns the daily clearness index according to 
    B. Ridley, J. Boland, and P. Lauret. 
    Modelling of diffuse solar fraction with multiple predictors. 
    Renewable Energy, 35:478–483, 2010. doi: 10.1016/j.renene.2009.07.018.

    Parameters
    ----------
    list_I : list of floats
        Measured global radiations on horizontal plane during the day.
    day : int
        day number between 1 and 365.
    time_zone : int
        fuseau_horaire.
    latitude : float
        Latitude in degrees.

    Returns
    -------
    float
        Daily clearness index (dimensionless).

    """
    l_io = [I0(h, day, time_zone, latitude) for h in range(24)]
    return sum(list_I)/sum(l_io)


def persistence_factor(G,G_plus1,G_minus1, 
                           hour, day, time_zone, latitude,Isc=1366.1):
    """
    Returns the persistence factor according to
    B. Ridley, J. Boland, and P. Lauret. 
    Modelling of diffuse solar fraction with multiple predictors. 
    Renewable Energy, 35:478–483, 2010. doi: 10.1016/j.renene.2009.07.018.


    Parameters
    ----------
    G : float
        Measured global radiations on horizontal plane (W/m2) at hour h.
    G_plus1 : float
        Measured global radiations on horizontal plane (W/m2) at hour h+1.
    G_minus1 : float
        Measured global radiations on horizontal plane (W/m2) at hour h-1.
    hour : int
        hour of the day between 0 and 23.
    day : int
        day number between 1 and 365.
    time_zone : int
        fuseau_horaire.
    latitude : float
        Latitude in degrees.
    Isc : float, optional
        Total solar irradiance. The default is 1366.1 W/m2 according to 
        C. Frohlich. Solar irradiance variability since 1978. 
        Space Science Reviews, 25(23):43774380, 2006.

    Returns
    -------
    res : float
        persistence factor (dimensionless).

    """
    k = kt(G, hour, day, time_zone, latitude,Isc)
    k_plus1 = kt(G_plus1, hour+1, day, time_zone, latitude, Isc)
    k_minus1 = kt(G_minus1, hour-1, day, time_zone, latitude, Isc)
    if k==0 and k_plus1 >0:
        res=k_plus1
    elif k == 0 and k_minus1 >0 :
        res=k_minus1
    else :
        res = (k_plus1+k_minus1)/2
    
    return res

def D_BRL(list_I, hour, day, time_zone, latitude, longitude, Isc=1366.1):
    """
    Returns the estimated diffuse radiation on horizontal plane according to
    B. Ridley, J. Boland, and P. Lauret. 
    Modelling of diffuse solar fraction with multiple predictors. 
    Renewable Energy, 35:478–483, 2010. doi: 10.1016/j.renene.2009.07.018.

    Parameters
    ----------
    list_I : list of floats
        Measured global radiations on horizontal plane during the day.
    hour : int
        hour of the day between 0 and 23.
    day : int
        day number between 1 and 365.
    time_zone : int
        fuseau_horaire.
    latitude : float
        Latitude in degrees.
    longitude : float
        Longitude in degrees.
    Isc : float, optional
        Total solar irradiance. The default is 1366.1 W/m2 according to 
        C. Frohlich. Solar irradiance variability since 1978. 
        Space Science Reviews, 25(23):43774380, 2006.

    Returns
    -------
    float
        Modelled diffuse radiation on horizontal plane (W/m2).

    """
    k=kt(list_I[hour], hour, day, time_zone, latitude, Isc)
    As=apparent_solar_time(hour, day, time_zone, longitude)
    phi = solar_elevation(hour, day, time_zone, latitude)
    k_daily = kt_daily(list_I, day, time_zone, latitude)
    psi=persistence_factor(list_I[hour], list_I[hour+1], list_I[hour-1], hour, day, time_zone, latitude)
    a = -5.32+7.28*k-0.03*As-0.0047*phi+(1.72*k_daily)+1.08*psi
    return list_I[hour+1]/(1+np.exp(a))



def B_BRL(list_I, hour, day, time_zone, latitude, longitude, Isc=1366.1):
    """
    Returns the estimated direct radiation on horizontal plane according to
    B. Ridley, J. Boland, and P. Lauret. 
    Modelling of diffuse solar fraction with multiple predictors. 
    Renewable Energy, 35:478–483, 2010. doi: 10.1016/j.renene.2009.07.018.
    
    Not really used (a simple columns difference is made).

    Parameters
    ----------
    list_I : list of floats
        Measured global radiations on horizontal plane during the day.
    hour : int
        hour of the day between 0 and 23.
    day : int
        day number between 1 and 365.
    time_zone : int
        fuseau_horaire.
    latitude : float
        Latitude in degrees.
    longitude : float
        Longitude in degrees.
    Isc : float, optional
        Total solar irradiance. The default is 1366.1 W/m2 according to 
        C. Frohlich. Solar irradiance variability since 1978. 
        Space Science Reviews, 25(23):43774380, 2006.

    Returns
    -------
    float
        Modelled diffuse radiation on horizontal plane (W/m2).

    """
    return list_I[hour+1] - D_BRL(list_I, hour, day, time_zone, latitude, longitude,Isc)








