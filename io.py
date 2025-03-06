# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 17:18:07 2025

@author: thibault.chevilliet
"""

import pandas as pd
import os
# from .BRL import *
from ladybug.epw import EPW
from ladybug.location import Location
# from ladybug.datacollection import HourlyContinuousCollection
# from ladybug.sunpath import Sunpath
# from ladybug.datatype.temperature import Temperature
# from ladybug.datatype.fraction import Fraction, RelativeHumidity
# from ladybug.datatype.speed import Speed
# from ladybug.datatype.angle import Angle
# from ladybug.datatype.energyflux import EnergyFlux
# from ladybug.datatype.illuminance import Illuminance
# from ladybug.datatype.pressure import Pressure
# from ladybug.datatype.distance import Distance
# from ladybug.psychrometrics import rel_humid_from_db_dpt #

# Required Field to build the epw file 
#(https://climate.onebuilding.org/papers/EnergyPlus_Weather_File_Format.pdf)
#The field described as not currently used in EnergyPlus calculation are
# omitted except for the GHradiation that csv source file contains 
output_columns = ['year','month','day','hour','dry_bulb_temperature',
                  'dew_point_temperature', 'relative_humidity',
                  'atmospheric_station_pressure', 
                  # 'Horizontal Infrared Radiation Intensity',
                  # 'Global Horizontal Radiation',
                  'direct_normal_radiation',
                  'diffuse_horizontal_radiation', 'wind_direction',
                  'wind_speed', 'total_sky_cover','opaque_sky_cover'
                  # 'Present Weather Observation','Present Weather Codes',
                  # 'Snow Depth','Liquid Precipitation Depth'
                  ]

# Dictionnary with source file headers and conversion factors
header_translate = {'T' : ('dry_bulb_temperature',1.0),
                    'TD':('dew_point_temperature',1.0),
                    'U':('relative_humidity',1.0), 
                    'PSTAT' : ('atmospheric_station_pressure',0.1), #hPa to kPa
                    'GLO' : ('global_horizontal_radiation',10000/3600),#J/cm2 to Wh/m2
                    'DD' : ('wind_direction',1),'FF' : ('wind_speed',1.0),
                    'N' : ('total_sky_cover',1.25), #octas to tenth
                    'DIR' : ('direct_normal_radiation',10000/3600),#J/cm2 to Wh/m2
                    'DIF' : ('diffuse_horizontal_radiation',10000/3600),#J/cm2 to Wh/m2
                    'NBAS' : ('Nl',1.25), #octas to tenth
                    'N1' : ('Nm',1.25), #octas to tenth
                    'N2' : ('Nh',1.25), #octas to tenth, N3 is neglected
                    }



class StationWeather:
    
    def __init__(self,name : str = None,station : str = None,
               period : tuple = (None,None),latitude : float = None,
               longitude : float = None,altitude : str = None,
               data : pd.DataFrame() = None,output_df = pd.DataFrame(
                   columns= output_columns),
               epw = None, translator : dict = header_translate,
               time_zone : int = None) :
        
        self.name = name
        self.station = station
        self.period = period
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.data = data
        self.output_df = output_df 
        self.epw = epw
        self.translator = translator
        self.time_zone = time_zone
    
    def wmo_code_to_epw_code(self,path_to_table) :
        converter = pd.read_csv(path_to_table
                                ,sep=','
                                ,dtype={'WW':int,
                                        'Present Weather Observation' : int,
                                        'Present Weather Codes': str}
                                ).set_index('WW')
        for i in self.data.index :
            tmp = self.data.at[i,'WW']
            self.data.at[i,'Present Weather Observation'] = converter.at[tmp,'Present Weather Observation']
            self.data.at[i,'Present Weather Codes'] = converter.at[tmp,'Present Weather Codes']

    def import_source(self,path,station_name,translate = header_translate) :
        
        df = pd.read_csv(path, sep=',')
        
        df['year'] = [int(str(x)[:4]) for x in df['AAAAMMJJHH']]
        df['month'] = [int(str(x)[4:6]) for x in df['AAAAMMJJHH']]
        df['day'] = [int(str(x)[6:8]) for x in df['AAAAMMJJHH']]
        df['hour'] = [int(str(x)[8:10]) for x in df['AAAAMMJJHH']]
        df.drop(['AAAAMMJJHH'],axis=1,inplace=True)

        self.data=df[df['NOM_USUEL']==station_name]
        self.data.reset_index(drop=True,inplace =True)
        for k in translate.keys():
            self.data[k]=self.data[k].fillna(0) #Avoid empty columns, better solution to be found
            self.data[k]=self.data[k].apply(lambda x: x*translate[k][1])
        self.data.rename(columns=
                         {k : v[0] for k,v in translate.items()},inplace=True)
    
    def localize(self,time_zone) :
        if self.data is None :
            raise TypeError('No data. import_source must be used first.')
        else :
            self.latitude = float(self.data['LAT'][0])
            self.longitude = float(self.data['LON'][0])
            self.altitude = float(self.data['ALTI'][0])
            self.time_zone = time_zone
    
    def time_slicer(self,year):

        self.data.drop(self.data[self.data.year != year].index, inplace=True)
        self.data.reset_index(drop=True,inplace=True)
                
    # def eval_data(self):
    #     A IMPLEMENTER : fonction qui regarde si toutes les données attendues 
    #     dans output sont présentes
        
    
    def gap_fill(self) :

        # # We fill sky covers with 0 when NaN
        # self.data[['total_sky_cover','Nl','Nm','Nh']] = self.data[
        #     ['total_sky_cover','Nl','Nm','Nh']].fillna(value=0) #Already done in import for total sky cover
        # We assume that total sky cover = opaque sky cover = "nébulosité" (seems to be done in existing epw files)
        self.data['opaque_sky_cover'] =self.data['total_sky_cover']
        #We create a DAY column which is the day between 0 and 365
        self.data['DAY'] = self.data['day'] #initialize
                
        # df[['a', 'b']] = df[['a','b']].fillna(value=0)
        for i in self.data.index :
            self.data.at[i,'DAY'] = DAY(self.data.at[i,'day'],self.data.at[i,'month'])
        
        for i in self.data.index :
            
            list_glob_rad = list(
                self.data['global_horizontal_radiation'][self.data['DAY']==self.data.at[i,'DAY']])
            list_glob_rad = [0]+list_glob_rad+[0] #Avoid problems
            self.data.at[i,'diffuse_horizontal_radiation']=D_BRL(
                list_glob_rad,
                self.data.at[i,'hour'],self.data.at[i,'DAY'],
                self.time_zone,self.latitude,self.longitude
                )
            self.data.at[i,'direct_normal_radiation']=self.data.at[i,'global_horizontal_radiation'] - self.data.at[i,'diffuse_horizontal_radiation']
        
    def to_epw(self,path):
        required_fields =['dry_bulb_temperature','dew_point_temperature',
                          'relative_humidity','atmospheric_station_pressure',
                          'direct_normal_radiation',
                          'diffuse_horizontal_radiation','wind_direction',
                          'wind_speed','total_sky_cover','opaque_sky_cover']
        
        self.epw = EPW.from_missing_values()
        self.epw.location = Location(city='Paris',country='France',
                                     latitude=self.latitude,
                                     longitude=self.longitude)
        for field in required_fields :
            getattr(self.epw, field).values = list(self.data[field])
        
        self.epw.write(path)
        
        

