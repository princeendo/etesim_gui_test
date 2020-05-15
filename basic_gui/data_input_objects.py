# -*- coding: utf-8 -*-
"""
Created on Fri May  8 13:26:29 2020

@author: cwhite
"""

import numpy as np
import pandas as pd
from collections import namedtuple

EastNorthUp = namedtuple('EastNorthUp', ['east', 'north', 'up'])
EarthCenterEarthFixed = namedtuple('EarthCenterEarthFixed', ['x', 'y', 'z'])
LatLonAlt = namedtuple('LatLonAlt', ['lat', 'lon', 'alt'])


class ETESim_Input():
    def __init__(self, inpDir):
        pass


class FixedAsset():
    def __init__(self, simulation, name, category, unique_id, run_number, *,
                 ecef=None, lla=None, enu=None):
        if all((x is None for x in (ecef, lla, enu))):
            raise ValueError('Must enter a valid coordinate!')

        self.sim = simulation
        self.name = name
        self.type = category
        self.id = unique_id
        self.runnum = run_number
        self.x, self.y, self.z = [None] * 3
        self.lat, self.lon, self.alt = [None] * 3
        self.east, self.north, self.up = [None] * 3
        if ecef is not None:
            self.set_ecef(*ecef)
            self.gen_lla()
        if lla is not None:
            self.set_lla(*lla)
            self.gen_ecef()
        if enu is not None:
            self.east, self.north, self.up = enu

    def set_ecef(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    def set_lla(self, lat, lon, alt):
        self.lat, self.lon, self.alt = lat, lon, alt

    def set_enu(self, east, north, up):
        self.east, self.north, self.up = east, north, up

    def gen_ecef(self, ):
        if None not in (self.x, self.y, self.z):
            return
        elif None not in (self.lat, self.lon, self.alt):
            self.x, self.y, self.z = lla2ecef(self.lat, self.lon, self.alt)
        else:
            raise ValueError('No valid input to generate!')

    def gen_enu(self, ref_lat, ref_lon, ref_alt):
        enu = lla2enu(self.lat, self.lon, self.alt,
                      ref_lat, ref_lon, ref_alt)

        self.east, self.north, self.up = enu

    def gen_lla(self, ):
        if None not in (self.lat, self.lon, self.alt):
            return
        elif None not in (self.x, self.y, self.z):
            self.lat, self.lon, self.alt = ecef2lla(self.x, self.y, self.z)
        else:
            raise ValueError('No valid input to generate!')

    def __eq__(self, asset):
        if self.sim != asset.sim:
            return False
        if self.name != asset.name:
            return False
        if self.type != asset.type:
            return False

        pairs = [(self.x, asset.x),
                 (self.y, asset.y),
                 (self.z, asset.z),
                 (self.lat, asset.lat),
                 (self.lon, asset.lon),
                 (self.alt, asset.alt),
                 (self.east, asset.east),
                 (self.north, asset.north),
                 (self.up, asset.up)]

        for (a, b) in pairs:
            if a is None and b is not None:
                return False
            if b is None and a is not None:
                return False
            if a != b:
                return False

        return True

    def df(self, index=0):
        dict_ = {'sim': self.sim,
                 'run': self.runnum,
                 'name': self.name,
                 'category': self.type,
                 'id': self.id,
                 'x': self.x,
                 'y': self.y,
                 'z': self.z,
                 'lat': self.lat,
                 'lon': self.lon,
                 'alt': self.alt,
                 'east': self.east,
                 'north': self.north,
                 'up': self.up, }

        return pd.DataFrame(dict_, index=[index])


class ENU():
    def __init__(self, east, north, up):
        self.east = east
        self.north = north
        self.up = up

    def array(self):
        return np.array([self.east, self.north, self.up])

    def norm(self):
        return np.linalg.norm(self.array())

    def to_ecef(self, refLat, refLon, refAlt):
        return enu2ecef(self.east, self.north, self.up, refLat, refLon, refAlt)

    def to_lla(self, refLat, refLon, refAlt):
        x, y, z = self.to_ecef(refLat, refLon, refAlt)
        return ecef2lla(x, y, z,)

    def __sub__(self, other_enu):
        return self + (-other_enu)

    def __add__(self, other_enu):
        otherEast, otherNorth, otherUp = other_enu.array()
        east = self.east + otherEast
        north = self.north + otherNorth
        up = self.up + otherUp
        return ENU(east, north, up)

    def __hash__(self):
        return hash((self.east, self.north, self.up))

    def __eq__(self, otherENU):
        return all(np.isclose(self.array(), otherENU.array()))

    def __lt__(self, other):
        # Case 0: a ~= b
        if self == other:
            return False

        # Case 1: a0 < b0
        if self.east < other.east and not np.isclose(self.east, other.east):
            return True
        # Case 2: a0 > b0
        if self.east > other.east and not np.isclose(self.east, other.east):
            return False
        # Case 3: a0 ~= b0, a1 < b1
        if self.north < other.north and not np.isclose(self.north,
                                                       other.north):
            return True
        # Case 4: a0 ~= b0, a1 > b1
        if self.north > other.north and not np.isclose(self.north,
                                                       other.north):
            return False
        # Case 5: a0 ~= b0, a1 > b1
        if self.north > other.north and not np.isclose(self.north,
                                                       other.north):
            return False
        # Case 6: a0 ~= b0, a1 ~= b1, a2 < b2
        if self.up < other.up and not np.isclose(self.up, other.up):
            return True
        # Case 7: a0 ~= b0, a1 ~= b1, a2 > b2
        if self.up > other.up and not np.isclose(self.up, other.up):
            return False

        # This should never occur
        return False

    def __le__(self, otherENU):
        return self < otherENU or self == otherENU

    def __gt__(self, otherENU):
        return not (self <= otherENU)

    def __ge__(self, otherENU):
        return not (self < otherENU)

    def __neg__(self,):
        return ENU(-self.east, -self.north, -self.up)

    def __abs__(self):
        return ENU(*np.abs(self.array()))

    def __repr__(self):
        _val = EastNorthUp(self.east, self.north, self.up)
        return f'{_val}'


def ecef2enu(objECEF, refECEF):
    refLat, refLon, _ = ecef2lla(refECEF)
    v = objECEF - refECEF

    T = ecef2enuMatrix(refLat, refLon)

    east, north, up = np.squeeze(np.asarray(T @ v))

    return np.array([east, north, up])


def lla2enu(objLat, objLon, objAlt, refLat, refLon, refAlt):
    refECEF = lla2ecef(refLat, refLon, refAlt)
    objECEF = lla2ecef(objLat, objLon, objAlt)
    v = (objECEF - refECEF)

    T = ecef2enuMatrix(refLat, refLon)

    east, north, up = np.squeeze(np.asarray(T @ v))

    return np.array([east, north, up])


def ecef2enuMatrix(refLat, refLon,):
    sinLat = np.sin(np.radians(refLat))
    cosLat = np.cos(np.radians(refLat))
    sinLon = np.sin(np.radians(refLon))
    cosLon = np.cos(np.radians(refLon))

    row1 = [-sinLon, cosLon, 0]
    row2 = [-sinLat * cosLon, -sinLat * sinLon, cosLat]
    row3 = [cosLat * cosLon, cosLat * sinLon, sinLat]
    A = np.matrix([row1, row2, row3])

    return A


def enu2ecefMatrix(refLat, refLon):
    return ecef2enuMatrix(refLat, refLon).transpose()


def enu2ecef(objEast, objNorth, objUp, refLat, refLon, refAlt):
    refLoc = lla2ecef(refLat, refLon, refAlt)
    v = np.array([objEast, objNorth, objUp])
    T = enu2ecefMatrix(refLat, refLon)

    u = T @ v
    return u + refLoc


def ecef2lla(x, y, z,
             radius=6378137.0,
             flattening=.0033528106647474805,
             eccentricity=0.08181919084261345):
    a, e, f = radius, eccentricity, flattening
    b = a * (1 - f)
    r = np.sqrt(x**2 + y**2)
    ePrimeSquared = (a ** 2 - b ** 2) / (b ** 2)
    F = 54 * (b ** 2) * (z ** 2)
    G = (r ** 2) + (1 - e ** 2) * (z ** 2) - (e ** 2) * (a ** 2 - b ** 2)
    c = ((e ** 4) * F * (r ** 2)) / (G ** 3)
    s = np.power(1 + c + np.sqrt(c ** 2 + 2 * c), 1 / 3)
    P = F / (3 * ((1 + s + 1 / s) ** 2) * (G ** 2))
    Q = np.sqrt(1 + 2 * P * (e ** 4))
    r0_1 = -(P * r * e * e) / (1 + Q)
    r0_2a = 0.5 * a * a * (1 + 1/Q)
    r0_2b = -P * z * z * (1 - e * e) / (Q * (1 + Q))
    r0_2c = -0.5 * P * r * r

    r0 = r0_1 + np.sqrt(r0_2a + r0_2b + r0_2c)

    qty1 = (r - r0 * e * e) ** 2

    U = np.sqrt(qty1 + (z ** 2))
    V = np.sqrt(qty1 + (z ** 2) * (1 - e * e))

    qty2 = (b ** 2) / (a * V)

    z0 = z * qty2
    alt = U * (1 - qty2)
    lat = np.degrees(np.arctan((z + ePrimeSquared * z0) / r))
    lon = np.degrees(np.arctan2(y, x))
    return np.array([lat, lon, alt])


def lla2ecef(lat, lon, alt):
    rad = np.float64(6378137.0)        # Radius of the Earth (in meters)
    f = np.float64(1.0/298.257223563)  # Flattening factor WGS84 Model
    cosLat = np.cos(np.radians(lat))
    sinLat = np.sin(np.radians(lat))
    FF = (1.0-f)**2
    C = 1/np.sqrt(cosLat**2 + FF * sinLat**2)
    S = C * FF

    x = (rad * C + alt) * cosLat * np.cos(np.radians(lon))
    y = (rad * C + alt) * cosLat * np.sin(np.radians(lon))
    z = (rad * S + alt) * sinLat
    return np.array([x, y, z])
