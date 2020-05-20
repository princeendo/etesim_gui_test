# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from collections import namedtuple

# For type hints
from typing import List, NewType
Vector = List[float]
Matrix = NewType('Matrix', float)

EastNorthUp = namedtuple('EastNorthUp', ['east', 'north', 'up'])
EarthCenterEarthFixed = namedtuple('EarthCenterEarthFixed', ['x', 'y', 'z'])
LatLonAlt = namedtuple('LatLonAlt', ['lat', 'lon', 'alt'])


class ETESim_Input():
    def __init__(self, inpDir):
        pass


class FixedAsset():
    def __init__(self, simulation: str, name: str, category: str,
                 unique_id: int, run_number: int, *,
                 ecef: Vector = None, lla: Vector = None,
                 enu: Vector = None) -> None:
        """
        A class for handling fixed assets. Stores metadata and locations
        in several possible coordinate systems.

        Parameters
        ----------
        simulation : str
            The simulation which generated the asset.
        name : str
            The name of the asset.
        category : str
            The category (e.g., radar) of the asset.
        unique_id : int
            An ID often specified by the simulation.
        run_number : int
            The run number, often specified by the simulation.
        ecef : Vector, optional
            ECEF asset coordinates (in meters) as 3-tuple. The default is None.
        lla : Vector, optional
            Latitude (deg), Longitude (deg), and Altitude (m)
            asset coordinates as 3-tuple. The default is None.
        enu : Vector, optional
             ENU asset coordinates (in meters) as 3-tuple. The default is None.

        Raises
        ------
        ValueError
            If no coordinate system is specified, the instance is invalid.

        Returns
        -------
        None

        """

        # A coordinate system must be specified or an error is thrown
        if all((x is None for x in (ecef, lla, enu))):
            raise ValueError('Must enter a valid coordinate!')

        self.sim = simulation
        self.name = name
        self.type = category
        self.id = unique_id
        self.runnum = run_number

        # Presetting all coordinate values to None
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

    def set_ecef(self, x: float, y: float, z: float) -> None:
        """
        Sets the ECEF location of the asset.

        Parameters
        ----------
        x : float
            The x location in meters
        y : float
            The y location in meters
        z : float
            The z location in meters

        Returns
        -------
        None

        """
        self.x, self.y, self.z = x, y, z

    def set_lla(self, lat: float, lon: float, alt: float) -> None:
        """
        Sets the latitude, longitude, and altitude of the asset.

        Parameters
        ----------
        lat : float
            The latitude location in degrees
        lon : float
            The longitude location in degrees
        alt : float
            The altitude location in meters

        Returns
        -------
        None

        """
        self.lat, self.lon, self.alt = lat, lon, alt

    def set_enu(self, east: float, north: float, up: float) -> None:
        """
        Sets the ENU location of the asset.

        Parameters
        ----------
        east : float
            The east location in meters
        north : float
            The north location in meters
        up : float
            The up location in meters

        Returns
        -------
        None

        """
        self.east, self.north, self.up = east, north, up

    def gen_ecef(self) -> None:
        """
        Generates ECEF XYZ coordinates for the class instance given
        Latitude (deg), Longitude (deg), and Altitude (m) coordinates
        coordinates for the instance given the following conditions:
            (1) ECEF coordinates do not already exist
            (2) Lat/Lon/Alt coordinates exist

        Raises
        ------
        ValueError
            If Lat/Lon/Alt values do not exist and ECEF values do not
            exist, there is no valid way to generate the coordinates.

        Returns
        -------
        None

        """
        if None not in (self.x, self.y, self.z):
            return
        elif None not in (self.lat, self.lon, self.alt):
            self.x, self.y, self.z = lla2ecef(self.lat, self.lon, self.alt)
        else:
            raise ValueError('No valid input to generate!')

    def gen_enu(self, refLat: float, refLon: float, refAlt: float) -> None:
        """
        Generates ENU coordinates for the asset given the
        latitude (deg), longitude (deg), and altitude (m) coordinates
        for the origin.

        Parameters
        ----------
        refLat : float
            The reference latitude in degrees.
        refLon : float
            The reference longitude in degrees.
        refAlt : float
            The reference altitude in meters.

        Returns
        -------
        None

        """
        self.east, self.north, self.up = lla2enu(self.lat, self.lon, self.alt,
                                                 refLat, refLon, refAlt)

    def gen_lla(self) -> None:
        """
        Generates Latitude (deg), Longitude (deg), and Altitude (m)
        coordinates for the instance given the following conditions:
            (1) Lat/Lon/Alt coordinates do not already exist
            (2) ECEF Coordinates exist

        An error is raised if neither condition (1) or (2) are valid.

        Raises
        ------
        ValueError
            If Lat/Lon/Alt values do not exist and ECEF values do not
            exist, there is no valid way to generate the coordinates.

        Returns
        -------
        None

        """
        if None not in (self.lat, self.lon, self.alt):
            return
        elif None not in (self.x, self.y, self.z):
            self.lat, self.lon, self.alt = ecef2lla(self.x, self.y, self.z)
        else:
            raise ValueError('No valid input to generate!')

    def __eq__(self, asset) -> bool:
        """
        Overloads the "=" operator to determine instance equality.
        Instances are considered equal if all these criteria are met:
            (1) They are generated by the same simulation
            (2) They have the same name
            (3) They have the same type (category)
            (4) Each member variable describing coordinate data matches

        Parameters
        ----------
        asset : FixedAsset
            An instance of the FixedAsset class

        Returns
        -------
        bool
            True if assets are equal, False otherwise

        """
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

    def df(self, index: int = 0) -> pd.DataFrame:
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
    def __init__(self, east: float, north: float, up: float) -> None:
        """
        A class for handling ENU coordinates

        Parameters
        ----------
        east : float
            The east location in meters
        north : float
            The north location in meters
        up : float
            The up location in meters

        Returns
        -------
        None

        """
        self.east = east
        self.north = north
        self.up = up

    def array(self) -> Vector:
        """
        Represents the elements as an array for easier interfacing with
        existing methods in other packages and classes.

        Returns
        -------
        Vector
            Elements are (east, north, up)

        """
        return np.array([self.east, self.north, self.up])

    def norm(self) -> float:
        """
        Generates the magnitude of the ENU vector.

        Returns
        -------
        float
            The 2-Norm of the vector

        """
        return np.linalg.norm(self.array())

    def to_ecef(self, refLat: float, refLon: float, refAlt: float) -> Vector:
        """
        Generates ECEF XYZ coordinates when the ENU origin is given as
        Latitude (deg), Longitude (deg), Altitude (m).

        Parameters
        ----------
        refLat : float
            The reference latitude in degrees.
        refLon : float
            The reference longitude in degrees.
        refAlt : float
            The reference altitude in meters.

        Returns
        -------
        Vector
            Elements are (latitude, longitude, altitude)

        """
        return enu2ecef(self.east, self.north, self.up, refLat, refLon, refAlt)

    def to_lla(self, refLat: float, refLon: float, refAlt: float) -> Vector:
        """
        Generates a Latitude (deg), Longitude (deg), Altitude (m)
        representation of the coordinates when the ENU origin is given as
        Latitude (deg), Longitude (deg), Altitude (m).

        Parameters
        ----------
        refLat : float
            The reference latitude in degrees.
        refLon : float
            The reference longitude in degrees.
        refAlt : float
            The reference altitude in meters.

        Returns
        -------
        Vector
            Elements are (latitude, longitude, altitude)

        """
        x, y, z = self.to_ecef(refLat, refLon, refAlt)
        return ecef2lla(x, y, z,)

    def __sub__(self, other_enu):
        """
        Overloads the "-" operator to define addition.

        In this case, O = A - B has the property:
            O.east = A.east - B.east
            O.north = A.north - B.north
            O.up = A.up - B.up

        Parameters
        ----------
        other_enu : ENU
            An instance of ENU

        Returns
        -------
        ENU
            An instance of ENU

        """
        return self + (-other_enu)

    def __add__(self, other_enu):
        """
        Overloads the "+" operator to define addition.

        In this case, O = A + B has the property:
            O.east = A.east + B.east
            O.north = A.north + B.north
            O.up = A.up + B.up

        Parameters
        ----------
        other_enu : ENU
            An instance of ENU

        Returns
        -------
        ENU
            An instance of ENU

        """
        otherEast, otherNorth, otherUp = other_enu.array()
        east = self.east + otherEast
        north = self.north + otherNorth
        up = self.up + otherUp
        return ENU(east, north, up)

    def __hash__(self) -> int:
        """
        Generates a hash from the member variables of this class.
        Class instances containing the same values for each variable
        will be considered identical. This would create a naive sorting
        algorithm.

        Currently, this is unused.

        Returns
        -------
        int
            The resulting hash

        """
        return hash((self.east, self.north, self.up))

    def __eq__(self, otherENU) -> bool:
        return all(np.isclose(self.array(), otherENU.array()))

    def __lt__(self, other) -> bool:
        """
        Overloads the '<' operator and provides a way to order instances
        of the ENU class.

        This could have been accomplished by converting them to tuples
        and then calling the sort command on an array containing them both
        but, because of the likelihood of similar but not identical values
        due to rounding error, it made sense to leverage the .isclose()
        numpy method to check for equality.

        An instance A of ENU is "less than" an instance B of ENU if and only
        if one of the following holds:
        (1) A.east < B.east
        (2) A.east == B.east and A.north < B.north
        (3) A.east == B.east, A.north == B.north, and A.up < B.up

        In this case, comments use "~=" to imply approximate equality.

        Parameters
        ----------
        other : ENU
            An instance of the ENU class

        Returns
        -------
        bool
            Whether the other class is "less than" this class instance

        """
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
        # Case 5: a0 ~= b0, a1 ~= b1, a2 < b2
        if self.up < other.up and not np.isclose(self.up, other.up):
            return True
        # Case 6: a0 ~= b0, a1 ~= b1, a2 > b2
        if self.up > other.up and not np.isclose(self.up, other.up):
            return False

        # This should never occur
        return False

    def __le__(self, otherENU) -> bool:
        """
        Determines if the other class instance is less than or equal to
        this instance

        Parameters
        ----------
        otherENU : ENU
            An instance of the ENU class

        Returns
        -------
        bool
            Whether the other class instance is less than or equal to
            this instance

        """
        return ((self < otherENU) or (self == otherENU))

    def __gt__(self, otherENU) -> bool:
        """
        Determines if the other class instance is greater than this instance

        Parameters
        ----------
        otherENU : ENU
            An instance of the ENU class

        Returns
        -------
        bool
            Whether the other class instance is greater than this instance

        """
        
        return not (self <= otherENU)

    def __ge__(self, otherENU) -> bool:
        """
        Determines if the other class instance is greater than or equal to
        this instance

        Parameters
        ----------
        otherENU : ENU
            An instance of the ENU class

        Returns
        -------
        bool
            Whether the other class instance is greater than or equal to
            this class instance

        """
        return not (self < otherENU)

    def __neg__(self):
        """
        Generates a class instance that is the negation of each
        element in this instance

        Returns
        -------
        ENU
            A class instance whose elements are the additive inverses
            of the elements in this instance

        """
        return ENU(-self.east, -self.north, -self.up)

    def __abs__(self):
        """
        An instance where each element's magnitude is present instead
        of its value.

        Returns
        -------
        ENU
            A class instance with nonnegative values

        """
        return ENU(*np.abs(self.array()))

    def __repr__(self) -> str:
        """
        Displays instances of these class in a formatted way.

        Returns
        -------
        str
            The default display for namedtuples, in this case
            one of type EastNorthUp

        """
        _val = EastNorthUp(self.east, self.north, self.up)
        return f'{_val}'


def ecef2enu(objECEF: Vector, refECEF: Vector) -> Vector:
    """
    Converts ECEF coordinates to ENU coordinates

    Parameters
    ----------
    objECEF : Vector
        The ECEF location of the object to transform.
    refECEF : Vector
        The ECEF location of the origin.

    Returns
    -------
    Vector
        The ENU coordinates of the object.

    """

    refLat, refLon, _ = ecef2lla(refECEF)
    v = objECEF - refECEF

    T = ecef2enuMatrix(refLat, refLon)

    east, north, up = np.squeeze(np.asarray(T @ v))

    return np.array([east, north, up])


def lla2enu(objLat: float, objLon: float, objAlt: float,
            refLat: float, refLon: float, refAlt: float) -> Vector:
    """
    Converts coordinates in latitude, longitude, and altitude to
    ENU coordinates.

    Parameters
    ----------
    objLat : float
        Latitude of the object in degrees.
    objLon : float
        Longitude of the object in degrees.
    objAlt : float
        Altitude of the object in meters.
    refLat : float
        Latitude of the ENU origin in degrees.
    refLon : float
        Longitude of the ENU origin in degrees.
    refAlt : float
        Altitude of the ENU origin in meters.

    Returns
    -------
    Vector
        The coordinates in ENU.

    """

    refECEF = lla2ecef(refLat, refLon, refAlt)
    objECEF = lla2ecef(objLat, objLon, objAlt)
    v = (objECEF - refECEF)

    T = ecef2enuMatrix(refLat, refLon)

    east, north, up = np.squeeze(np.asarray(T @ v))

    return np.array([east, north, up])


def ecef2enuMatrix(refLat: float, refLon: float) -> Matrix:
    """
    Generates a matrix to transform ECEF coordinates to ENU coordinates.

    Parameters
    ----------
    refLat : float
        The ENU origin's latitude in degrees.
    refLon : float
        The ENU origin's longitude in degrees.

    Returns
    -------
    Matrix
        A 3x3 Numpy Matrix that is the transformation from ECEF to ENU

    """

    sinLat = np.sin(np.radians(refLat))
    cosLat = np.cos(np.radians(refLat))
    sinLon = np.sin(np.radians(refLon))
    cosLon = np.cos(np.radians(refLon))

    row1 = [-sinLon, cosLon, 0]
    row2 = [-sinLat * cosLon, -sinLat * sinLon, cosLat]
    row3 = [cosLat * cosLon, cosLat * sinLon, sinLat]
    A = np.matrix([row1, row2, row3])

    return A


def enu2ecefMatrix(refLat: float, refLon: float) -> Matrix:
    """
    Generates a matrix to transform ENU coordinates to ECEF coordinates.

    Parameters
    ----------
    refLat : float
        The ENU origin's latitude in degrees.
    refLon : float
        The ENU origin's longitude in degrees.

    Returns
    -------
    Matrix
        A 3x3 Numpy Matrix that is the transformation from ENU to ECEF

    """

    return ecef2enuMatrix(refLat, refLon).transpose()


def enu2ecef(objEast: float, objNorth: float, objUp: float,
             refLat: float, refLon: float, refAlt: float) -> Vector:
    """
    Converts ENU coordinates into ECEF coordinates.

    Parameters
    ----------
    objEast : float
        The object's ENU-East location
    objNorth : float
        The object's ENU-North location
    objUp : float
        The object's ENU-Up location
    refLat : float
        The ENU origin's latitude.
    refLon : float
        The ENU origin's longitude.
    refAlt : float
        The ENU origin's altitude.

    Returns
    -------
    Vector
        The coordinates in ECEF.

    """

    refLoc = lla2ecef(refLat, refLon, refAlt)
    v = np.array([objEast, objNorth, objUp])
    T = enu2ecefMatrix(refLat, refLon)

    u = T @ v
    return u + refLoc


def ecef2lla(x: float, y: float, z: float,
             radius: float = 6378137.0,
             flattening: float = 0.0033528106647474805,
             eccentricity: float = 0.08181919084261345) -> Vector:
    """
    Converts XYZ ECEF coordinates to latitude, longitude, and altitude.
    Uses WGS84 Earth parameters

    Parameters
    ----------
    x : float
        X coordinate in ECEF
    y : float
        Y coordinate in ECEF
    z : float
        Z coordinate in ECEF
    radius : float, optional
        The radius of the earth, in meters.
        The default is 6378137.0.
    flattening : float, optional
        The flattening constant of the earth.
        The default is 0.0033528106647474805.
    eccentricity : float, optional
        The eccentricity of the Earth ellipsoid model.
        The default is 0.08181919084261345.

    Returns
    -------
    Vector
        Latitude, longitude, and altitude of object in degrees, degrees,
        and meters, respectively

    """

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


def lla2ecef(lat: float, lon: float, alt: float) -> Vector:
    """
    Converts latitude/longitude/altitude coordinates to
    ECEF XYZ coordinates. Uses WGS84 Earth model.

    Parameters
    ----------
    lat : float
        Latitude of the object in degrees
    lon : float
        Longitude of the object in degrees
    alt : float
        Altitude of the object in meters

    Returns
    -------
    Vector
        The XYZ coordinates in ECEF

    """
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
