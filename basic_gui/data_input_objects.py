# -*- coding: utf-8 -*-
"""
Created on Fri May  8 13:26:29 2020

@author: cwhite
"""

import numpy as np

class ETESim_Input():
    def __init__(self, inpDir):
        pass

    
class FixedAsset():
    def __init__(self, simulation, category, unique_id, ecef=None, lla=None,
                 enu=None):
        self.sim = simulation
        self.type = category
        self.id = unique_id
        if ecef:
            self.x, self.y, self.z = ecef
            

class ENU():
    def __init__(self, east, north, up):
        self.east = east
        self.north = north
        self.up = up
    
    def to_ecef(self, refLat, refLon, refAlt):
        return lla2ecef(self.to_lla(refLat, refLon, refAlt))
    
    def to_lla(self, refLat, refLon, refAlt):
        pass
        
            
            
def lla2ecef(lat, lon, alt):
    
    rad = np.float64(6378137.0)        # Radius of the Earth (in meters)
    f = np.float64(1.0/298.257223563)  # Flattening factor WGS84 Model
    cosLat = np.cos(np.radians(lat))
    sinLat = np.sin(np.radians(lat))
    FF     = (1.0-f)**2
    C      = 1/np.sqrt(cosLat**2 + FF * sinLat**2)
    S      = C * FF

    x = (rad * C + alt) * cosLat * np.cos(np.radians(lon))
    y = (rad * C + alt) * cosLat * np.sin(np.radians(lon))
    z = (rad * S + alt) * sinLat
    return x, y, z