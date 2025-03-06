#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  4 12:03:29 2025

@author: thibault.chevilliet
"""
import BRL
import io
#%%
w=StationWeather()
w.name ='paris_montsouris'
p = "/home/thibault.chevilliet@enpc.fr/Documents/Fichiers_meteo/H_75_2010-2019.csv"
w.import_source(p,'PARIS-MONTSOURIS')
#%%
year = 2011
w.localize(1)
# w.wmo_code_to_epw_code()
w.time_slicer(year)
w.gap_fill()

w.to_epw(f"/home/thibault.chevilliet@enpc.fr/Documents/Fichiers_meteo/{year}_Montsouris.epw")

#%%

import matplotlib.pyplot as plt
fig,ax = plt.subplots()
start = DAY(1,4)
duration = 5

ax.plot(range(start*24,start*24+24*duration),
        w.data.global_horizontal_radiation[start*24:(start*24+24*duration)],c='blue')
ax.plot(range(start*24,start*24+24*duration),
        w.data.diffuse_horizontal_radiation[start*24:(start*24+24*duration)],c='orange')
ax.plot(range(start*24,start*24+24*duration),
        w.data.direct_normal_radiation[start*24:(start*24+24*duration)],c='green')


plt.show()