# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 17:18:07 2025

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
    # return h

# import matplotlib.pyplot as plt
# fig,ax = plt.subplots()
# ax.plot(range(24),[solar_elevation(h,172,1,48.86) for h in range(24)])
# # ax.plot(range(24),h)
# plt.show()

def gamma(hour,day,time_zone,latitude) :
    h = math.radians(solar_elevation(hour,day,time_zone, latitude))
    a = math.sin(h)
    return 1/(1+8*(a**0.7))

# import matplotlib.pyplot as plt
# fig,ax = plt.subplots()
# ax.plot(range(24),[gamma(h,172,1,48.86) for h in range(24)])
# # ax.plot(range(24),h)
# plt.show()

def cs_hor_direct_radiation(hor_global_rad,hour,day,time_zone,latitude) :
    """
    Returns the estimated direct radiation on an horizontal surface from the
    global radiation on an horizontal surface in clear sky conditions according 
    to Taesler, R., & Andersson, C. (1984). 
    A method for solar radiation computations using routine meteorological 
    observations. Energy Build.;(Switzerland), 7(4)

    Parameters
    ----------
    hor_global_rad : float
        Global radiation on horizontal surface.
    hour : int
        between 0 and 23.
    day : int
        between 0 and 365.
    time_zone : int
        between -24 and 24.
    latitude : float
        Latitude in degrees. Between -90° and 90°

    Returns
    -------
    float
        Direct radiation on horizontal plane (W/m2) in clear conditions sky.

    """
    h =math.radians(solar_elevation(hour,day,time_zone, latitude))
    if h == 0 :
        res = 0
    else :
        a = math.sin(h)
        res = hor_global_rad*(1-gamma(hour,day,time_zone,latitude))/a

    return res

def cs_hor_diffuse_radiation(hor_global_rad,hour,day,time_zone,latitude) :
    """
    Returns the estimated diffuse radiation on an horizontal surface from the
    global radiation on an horizontal surface in clear sky conditions according
    to Taesler, R., & Andersson, C. (1984). 
    A method for solar radiation computations using routine meteorological 
    observations. Energy Build.;(Switzerland), 7(4)

    Parameters
    ----------
    hor_global_rad : float
        Global radiation on horizontal surface.
    hour : int
        between 0 and 23.
    day : int
        between 0 and 365.
    time_zone : int
        between -24 and 24.
    latitude : float
        Latitude in degrees. Between -90° and 90°

    Returns
    -------
    float
        Diffuse radiation on horizontal plane (W/m2) in clear conditions sky.
    """
    h = math.radians(solar_elevation(hour,day,time_zone, latitude))
    a = math.sin(h)
    gamma = 1/(1+8*(a**0.7))
    return (gamma*hor_global_rad).real

def GHn_to_GH(hor_global_rad,total_sky_cover,Nl,Nm,Nh,Ag=0.25,Al=0.75,Am=0.45,Ah=0.40):
    
    if total_sky_cover==0:
        res = hor_global_rad
    else :
        Ac= 0.1*(Nl*Al+Nm*Am+Nh*Ah)
        res= (Ag*Ac-1)*hor_global_rad/(Ac-1)
    return res



def hor_direct_radiation(hor_global_rad,hour,day,time_zone,latitude,
                         total_sky_cover,Nl,Nm,Nh,
                         Ag=0.25 # We assume there is no snow on the ground, 0.8 else.
                         ,Al=0.75,Am=0.45,Ah=0.40):
    """
    Returns the estimated direct radiation on an horizontal surface from the
    global radiation on an horizontal surface according to
    Taesler, R., & Andersson, C. (1984). 
    A method for solar radiation computations using routine meteorological 
    observations. Energy Build.;(Switzerland), 7(4)

    Parameters
    ----------
    hor_global_rad : float
        Global radiation on horizontal surface.
    hour : int
        between 0 and 23.
    day : int
        between 0 and 365.
    time_zone : int
        between -24 and 24.
    latitude : float
        Latitude in degrees. Between -90° and 90°
    total_sky_cover : float
        total sky cover in tenth (octas in the article, but tenths in Ladybug).
    Nl : float
        low clouds sky cover in tenth (octas in the article, 
                                      but tenths in Ladybug).
    Nm : TYPE
        medium clouds sky cover in tenth (octas in the article, 
                                      but tenths in Ladybug).
    Nh : TYPE
        high clouds sky cover in tenth (octas in the article, 
                                      but tenths in Ladybug).
    Ag : float, optional
        Ground albedo. The default is 0.25 (according to the article).
    Al : TYPE, optional
        Low clouds albedo. The default is 0.75 (according to the article).
    Am : float, optional
        Medium clouds albedo. The default is 0.45 (according to the article).
    Ah : float, optional
        High clouds albedo. The default is 0.40 (according to the article).

    Returns
    -------
    float
        Direct radiation on horizontal plane (W/m2)

    """
    h = math.radians(solar_elevation(hour,day,time_zone, latitude))
    a = math.sin(h)
    factor = a*(1-(total_sky_cover/10))
    Gh = GHn_to_GH(hor_global_rad, total_sky_cover,Nl, Nm, Nh)
    return factor*cs_hor_direct_radiation(Gh, hour, day, time_zone, latitude)

# import matplotlib.pyplot as plt
# fig,ax = plt.subplots()
# ax.plot(range(24),[hor_direct_radiation(1000,h,172,1,48.86,6,4,1,0) for h in range(24)])
# # ax.plot(range(24),[cs_hor_direct_radiation(1000,h,172,1,48.86) for h in range(24)])
# # ax.plot(range(24),h)
# plt.show()


def hor_diffuse_radiation(hor_global_rad,hour,day,time_zone,latitude,
                         total_sky_cover,Nl,Nm,Nh,
                         Ag=0.25 # We assume there is no snow on the ground, 0.8 else.
                         ,Al=0.75,Am=0.45,Ah=0.40) :
    """
    Gives the estimated diffuse radiation on an horizontal surface from the
    global radiation on an horizontal surface according to
    Taesler, R., & Andersson, C. (1984). 
    A method for solar radiation computations using routine meteorological 
    observations. Energy Build.;(Switzerland), 7(4)

    Parameters
    ----------
    hor_global_rad : float
        Global radiation on horizontal surface.
    hour : int
        between 0 and 23.
    day : int
        between 0 and 365.
    time_zone : int
        between -24 and 24.
    latitude : float
        Latitude in degrees. Between -90° and 90°
    total_sky_cover : float
        total sky cover in tenth (octas in the article, but tenths in Ladybug).
    Nl : float
        low clouds sky cover in tenth (octas in the article, 
                                      but tenths in Ladybug).
    Nm : TYPE
        medium clouds sky cover in tenth (octas in the article, 
                                      but tenths in Ladybug).
    Nh : TYPE
        high clouds sky cover in tenth (octas in the article, 
                                      but tenths in Ladybug).
    Ag : float, optional
        Ground albedo. The default is 0.25 (according to the article).
    Al : TYPE, optional
        Low clouds albedo. The default is 0.75 (according to the article).
    Am : float, optional
        Medium clouds albedo. The default is 0.45 (according to the article).
    Ah : float, optional
        High clouds albedo. The default is 0.40 (according to the article).

    Returns
    -------
    float
        Direct radiation on horizontal plane (W/m2)

    """
    return hor_global_rad - hor_direct_radiation(hor_global_rad, hour, day,
                                                 time_zone, latitude, 
                                                 total_sky_cover, Nl, Nm, Nh)

# import matplotlib.pyplot as plt
# fig,ax = plt.subplots()
# ax.plot(range(24),[hor_diffuse_radiation(500,h,172,1,48.86) for h in range(24)])
# # ax.plot(range(24),h)
# plt.show()