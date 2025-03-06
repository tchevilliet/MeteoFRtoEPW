#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  6 12:18:03 2025

@author: thibault.chevilliet
"""

import math

def DAY(day,month):
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
        between -24 and 24.

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

def mass_air(hour, day, time_zone, latitude) :
    h=solar_elevation(hour, day, time_zone, latitude)
    sinh = math.sin(math.radians(h))
    return 1/(sinh+(0.50572/((h+6.07995)**1.6364)))

def Ct(day) :
    return 1+0.034*math.cos(math.radians(day-2))

def I0 (hour, day, time_zone, latitude,Isc=1366.1) :
    E0= Ct(day)
    h=solar_elevation(hour, day, time_zone, latitude)
    sinh = math.sin(math.radians(h))
    return E0*Isc*sinh

def kt(G_measured,hour, day, time_zone, latitude,Isc=1366.1) :
    
    Gextra = I0(hour, day, time_zone, latitude, Isc)
    if Gextra == 0 :
        res = 0
    else :
        res = G_measured/Gextra
    return res

def Knc(hour, day, time_zone, latitude) :
    mair = mass_air(hour, day, time_zone, latitude)
    return 0.866 - 0.122*mair + 0.0121*(mair**2)-0.000653*(mair**3)+0.000014*(mair**4)
import numpy as np
def deltaKn(G_measured, hour, day, time_zone, latitude, Isc=1366.1) :
    k = kt(G_measured,hour, day, time_zone, latitude, Isc)
    mair = mass_air(hour, day, time_zone, latitude)
    if k == 0:
        res = 0
        c=0
    elif k<=0.6 :
        a = 0.512 - 1.560*k + 2.286*(k**2) - 2.222*(k**3)
        b = 0.370 + 0.962*k
        c = -0.280 + 0.932*k - 20.048*(k**2)
        # res = a+b*np.exp(np.float128(c*mair))
    else :
        a = -5.743 + 21.77*k - 27.49*(k**2) + 11.56*(k**3)
        b = 41.4 - 118.5*k + 66.05*(k**2) +31.9*(k**3)
        c = -47.01 + 184.2*k - 222*(k**2) + 73.81*(k**3)
        # res = a+b*np.exp(np.float128(c*mair))
    return mair

import matplotlib.pyplot as plt
fig,ax = plt.subplots()
ax.plot(range(11,15),[deltaKn(100,h,0,1,48.86) for h in range(11,15)])
ax2 = ax.twinx()
# ax2.plot(range(24),[I0(h,172,1,48.86) for h in range(24)],c='r')
plt.show()

def Kn(G_measured, hour, day, time_zone, latitude,Isc=1366.1) :
    return Knc(hour, day, time_zone, latitude)-deltaKn(G_measured, hour, day, time_zone, latitude, Isc)

def B_DISC(G_measured, hour, day, time_zone, latitude, Isc=1366.1) :
    kn = Kn(G_measured, hour, day, time_zone, latitude, Isc)
    return I0(hour, day, time_zone, latitude)*kn

def D_DISC(G_measured, hour, day, time_zone, latitude,Isc=1366.1) :
    return G_measured-B_DISC(G_measured, hour, day, time_zone, latitude, Isc)








