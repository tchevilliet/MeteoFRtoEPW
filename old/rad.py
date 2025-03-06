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

def opt_air_mass(hour,day,time_zone,latitude) :
    h = solar_elevation(hour, day, time_zone, latitude)
    if h > 10 :
        res = 1/math.sin(math.radians(h))
    else : 
        res = 1.22*(1.0144/math.sin(math.radians(h+1.44))-0.49)
    return res

def Fowle(tsv,hour,day,time_zone,latitude) :
    return 70+2.8*tsv*opt_air_mass(hour,day,time_zone,latitude)

def Sc_prime(DAY,Scs=1370):
    """
    From Spitters and al 1986. Seems to be B' in Taesler 84.

    Parameters
    ----------
    DAY : TYPE
        DESCRIPTION.
    Scs : TYPE, optional
        DESCRIPTION. The default is 1370.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    return Scs*(1+0.033*math.cos(math.radians(360*DAY/365)))

def B(tsv,hour,day,time_zone,latitude,Scs=1370):
    return Sc_prime(day,Scs)-Fowle(tsv,hour,day,time_zone,latitude)

def Bhn(tsv,hour,day,time_zone,latitude,total_sky_cover,Scs=1370):
    return B(tsv, hour, day, time_zone, latitude)*math.sin(
        math.radians(solar_elevation(hour, day, time_zone, latitude)))*(1-total_sky_cover/10)

def Dhn(Ghn,tsv,hour,day,time_zone,latitude,total_sky_cover,Scs=1370) :
    return Ghn-Bhn(tsv, hour, day, time_zone, latitude, total_sky_cover)


def gamma(hour,day,time_zone,latitude) :
    a = math.sin(math.radians(solar_elevation(hour,day,time_zone, latitude)))
    return 1/(1+8*(a**0.7))

# import matplotlib.pyplot as plt
# fig,ax = plt.subplots()
# ax.plot(range(24),[gamma(h,10,1,48.86) for h in range(24)])
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
    return gamma(hour,day,time_zone,latitude)*hor_global_rad

def Ac(Nl,Nm,Nh,Al=0.75,Am=0.45,Ah=0.40):
    return min(0.1*(Nl*Al+Nm*Am+Nh*Ah),0.95)
    # return 0.1*(Nl*Al+Nm*Am+Nh*Ah)

# import numpy as np
# X = np.arange(0,11,1.25)
# Y= np.arange(0,11,1.25)

# Z=np.array([[Ac(x, y, 0) for x in X] for y in Y])

def f_ghn_to_gh(Alb_c,Ag=0.25) :
    return (Ag*Alb_c-1)/(Alb_c-1)

# import matplotlib.pyplot as plt
# import numpy as np
# fig,ax = plt.subplots()
# ax.plot(np.linspace(0,1,100),[f_ghn_to_gh(x) for x in np.linspace(0,1,100)])
# # ax.plot(range(24),h)
# plt.show()

def GHn_to_GH(GHn,total_sky_cover,factor):
    
    if total_sky_cover==0:
        res = GHn
    else :
        res= factor*GHn
    return res

def GH_to_BHn(GH, hour, day, time_zone, latitude, total_sky_cover):
    return GH*(1-gamma(hour, day, time_zone, latitude))*(1-(total_sky_cover/10))


    

# import matplotlib.pyplot as plt
# fig,ax = plt.subplots()
# for N in range(2,9) :
#     ax.plot(range(24),[GHn_to_GH(500,N,N-2,2,0) for h in range(24)])
#     # ax.plot(range(24),[cs_hor_direct_radiation(1000,h,172,1,48.86) for h in range(24)])
#     # ax.plot(range(24),h)
# ax.legend()
# plt.show()



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

    factor = (1-gamma(hour, day, time_zone, latitude))*(1-(total_sky_cover/10))
    Gh = GHn_to_GH(hor_global_rad, total_sky_cover,Nl, Nm, Nh,Ag,Al,Am,Ah)
    return factor*Gh

# import matplotlib.pyplot as plt
# fig,ax = plt.subplots()
# for N in range(1,4) :
#     ax.plot(range(24),[hor_direct_radiation(1000,h,172,1,48.86,N,N-2,2,0) for h in range(24)])
#     # ax.plot(range(24),[cs_hor_direct_radiation(1000,h,172,1,48.86) for h in range(24)])
#     # ax.plot(range(24),h)
# ax.legend()
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

def kt_daily(list_I,day, time_zone, latitude):
    # l_kt = [kt(i, h, day, time_zone, latitude) for i, h in zip(list_I,range(24))]
    l_io = [I0(h, day, time_zone, latitude) for h in range(24)]
    return sum(list_I)/sum(l_io)
    # return l_io

def apparent_solar_time(hour ,day, time_zone, longitude) :
    B = 360*(day-81)/365
    Et = 9.87*math.sin(math.radians(2*B))-7.53*math.cos(math.radians(B))-1.5*math.sin(math.radians(B))
    Tc = 4*(longitude-15*time_zone) + Et
    return hour+Tc/60

def global_radiation_level(G,G_plus1,G_minus1, hour, day, time_zone, latitude,Isc=1366.1):
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
    k=kt(list_I[hour], hour, day, time_zone, latitude, Isc)
    As=apparent_solar_time(hour, day, time_zone, longitude)
    phi = solar_elevation(hour, day, time_zone, latitude)
    k_daily = kt_daily(list_I, day, time_zone, latitude)
    psi=global_radiation_level(list_I[hour], list_I[hour+1], list_I[hour-1], hour, day, time_zone, latitude)
    a = -5.32+7.28*k-0.03*As-0.0047*phi+(1.72*k_daily)+1.08*psi
    return list_I[hour+1]/(1+math.exp(a))

# kt_daily(l_I, 201,1, 48.86)

def B_BRL(list_I, hour, day, time_zone, latitude, longitude, Isc=1366.1):
    return list_I[hour+1] - D_BRL(list_I, hour, day, time_zone, latitude, longitude,Isc)


