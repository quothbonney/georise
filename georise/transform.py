from typing import Tuple
from osgeo import gdal, osr, ogr
from geopy import Point
from . import util

class TerrainTransform:
    GeoTransformTuple = Tuple[float, float, float, float, float, float]

    def __init__(self, geo_transform: GeoTransformTuple, _xsz: int, _ysz: int) -> None:
        self.xo, self.weres, self.rowrot, self.yo, self.colrot, self.nsres = geo_transform
        self.xsz = _xsz;
        self.ysz = _ysz;

    def get(self):
        return (self.xo, self.weres, self.rowrot, self.yo, self.colrot, self.nsres , self.xsz, self.ysz)

    def get_size_meters(self):
        srs = osr.SpatialReference()
        srs.SetWellKnownGeogCS("WGS84")

        if None in self.get():
            raise TypeError("Uninitialized value None detected in geo transform. Call object repr to debug.")

        xmax = self.xo + (self.weres * self.xsz)
        ymax = self.yo + (self.nsres * self.ysz)
        print("MIN", self.xo, self.yo)
        print("MAX", xmax, ymax)

        xscale = util.get_distance_between_lat_lon_points_geopy(self.yo, self.xo, self.yo, xmax)  
        yscale = util.get_distance_between_lat_lon_points_geopy(self.yo, self.xo, ymax, self.xo) 

        return (xscale, yscale)

    def get_scale(self) -> Tuple[float, float, float]:
        srs = osr.SpatialReference()
        srs.SetWellKnownGeogCS("WGS84")

        if None in self.get():
            raise TypeError("Uninitialized value None detected in geo transform. Call object repr to debug.")

        xmax = self.xo + (self.weres * self.xsz)
        ymax = self.yo + (self.nsres * self.ysz)
        print("MIN", self.xo, self.yo)
        print("MAX", xmax, ymax)

        xscale = util.get_distance_between_lat_lon_points_geopy(self.yo, self.xo, self.yo, xmax) / self.ysz
        yscale = util.get_distance_between_lat_lon_points_geopy(self.yo, self.xo, ymax, self.xo) / self.xsz

        scale_tup = tuple((xscale / xscale, yscale / xscale, 1))
        return scale_tup 

    def validate_transform(self):
        # Check latitude boundry
        if (
            self.yo < -90 or 
            self.yo > 90
        ):
            print(f"WARNING: Latitude origin {self.yo} exceeds [-90, 90] boundry.")
            return False
        
        # Check longitude boundry
        if(
            self.xo < -180 or 
            self.xo > 180 
            ):
            print(f"WARNING: Longitude origin {self.xo} exceeds [-180, 180] boundry.")
            return False
        
        xmax = self.xo + (self.weres * self.xsz)
        ymax = self.yo + (self.nsres * self.ysz)

        # Check maximum latitude boundry
        if (
            ymax < -90 or 
            ymax > 90
        ):
            print(f"WARNING: Latitude maximum {self.yo} exceeds [-90, 90] boundry.")
            return False
        
        # Check maximum longitude mboundry
        if(
            xmax < -180 or 
            xmax > 180 
            ):
            print(f"WARNING: Longitude maximum {self.xo} exceeds [-180, 180] boundry.")
            return False
        

        return True 

    def __repr__(self) -> str:
        categories = ["X-Origin", "W-E Res.", "Row Rot.", "Y-Origin", "Column Rot.", "N-S Res.", "X-Size\t", "Y-Size\t"]
        values = self.get()

        repr_str = "".join([ categories[i] + "\t" + str(values[i]) + "\n" for i in range(len(values)) ])

        return repr_str
