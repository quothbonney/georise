from typing import Tuple
from osgeo import gdal, osr, ogr

class TerrainTransform:
    def __init__(self, geo_transform: Tuple[float, ...], _xsz: int, _ysz: int) -> None:
        self.xo, self.weres, self.rowrot, self.yo, self.colrot, self.nsres = geo_transform
        self.xsz = _xsz;
        self.ysz = _ysz;

    def get(self):
        return (self.xo, self.weres, self.rowrot, self.yo, self.colrot, self.nsres , self.xsz, self.ysz)

    def get_scale(self) -> Tuple[float, float, float]:
        srs = osr.SpatialReference()
        srs.SetWellKnownGeogCS("WGS84")

        if None in self.get():
            raise TypeError("Uninitialized value None detected in geo transform. Call object repr to debug.")

        xmax = self.xo + (self.weres * self.xsz)
        ymax = self.yo + (self.nsres * self.ysz)

        xscale = distance_between_points(self.xo, self.yo, self.xo, ymax) / self.ysz
        yscale = distance_between_points(self.xo, self.yo, xmax, self.yo) / self.xsz

        return (xscale, yscale, 1) 

    def __repr__(self) -> str:
        categories = ["X-Origin", "W-E Res.", "Row Rot.", "Y-Origin", "Column Rot.", "N-S Res.", "X-Size\t", "Y-Size\t"]
        values = self.get()

        repr_str = "".join([ categories[i] + "\t" + str(values[i]) + "\n" for i in range(len(values)) ])

        return repr_str