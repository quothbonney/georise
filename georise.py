import pyqtgraph as pg
import pyqtgraph.opengl as gl
from osgeo import gdal, osr, ogr
import numpy as np
import sys
import matplotlib.pyplot as plt
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from typing import Tuple


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

        def latlong_to_xy(lat, lon, target_srs):
            source_srs = osr.SpatialReference()
            source_srs.ImportFromEPSG(4326)

            transformation = osr.CoordinateTransformation(source_srs, target_srs)
            return transformation.TransformPoint(lon, lat)[:2]

        def distance_between_points(lat1, lon1, lat2, lon2):
            target_srs = osr.SpatialReference()
            target_srs.ImportFromEPSG(3857)  # WGS 84 / Pseudo-Mercator

            x1, y1 = latlong_to_xy(lat1, lon1, target_srs)
            x2, y2 = latlong_to_xy(lat2, lon2, target_srs)

            return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

        xscale = distance_between_points(self.xo, self.yo, self.xo, ymax) / self.ysz
        yscale = distance_between_points(self.xo, self.yo, xmax, self.yo) / self.xsz

        return (xscale, yscale, 1) 

    def __repr__(self) -> str:
        categories = ["X-Origin", "W-E Res.", "Row Rot.", "Y-Origin", "Column Rot.", "N-S Res.", "X-Size\t", "Y-Size\t"]
        values = self.get()

        repr_str = "".join([ categories[i] + "\t" + str(values[i]) + "\n" for i in range(len(values)) ])

        return repr_str

            
        

class GRDataProvider:
    data = {}
    __hash = 0

    @classmethod
    def increment_hash(cls):
       cls.__hash += 1 

    def add_terrain(self, fname: str) -> int:
        src = gdal.Open(fname, gdal.GA_ReadOnly)
        band = src.GetRasterBand(1)
        if not band:
            raise ValueError(f"No data in raster band {fname}")

        geo_transform = src.GetGeoTransform()
        transform_object = TerrainTransform(geo_transform, src.RasterXSize, src.RasterYSize)
        print("distance", transform_object.get_scale())
        print(repr(transform_object))
        tup = (transform_object, band.ReadAsArray())

        self.data[self.__hash] = tup

        return self.__hash


class GRRasterScene:
    app = QtWidgets.QApplication([])
    w = gl.GLViewWidget()
    prov = GRDataProvider()

    def __init__(self) -> None: 
        self.w.opts['distance'] = 10 
        self.w.setWindowTitle('pyqtgraph example: GLLinePlotItem')
        self.w.setGeometry(0, 0, 600, 600)
        self.w.show()

    def add_geometry(self, hash):
        data_tup = self.prov.data[hash]
        # arr = data_tup[1]
        x_sz, y_sz = data_tup[1].shape

        y = np.linspace(0, y_sz - 1, y_sz)
        x = np.linspace(0, x_sz - 1, x_sz)


        cmap = plt.get_cmap('twilight_shifted_r')
        minZ=np.min(data_tup[1])
        maxZ=np.max(data_tup[1])
        img = cmap((data_tup[1]-minZ)/(maxZ -minZ))
        
        surf = gl.GLSurfacePlotItem(x=y, y=x, z=data_tup[1], colors = img, shader='shaded')

        surf.setGLOptions('opaque')
        surf.setDepthValue(0)

        self.w.addItem(surf)




if __name__ == '__main__':
    scene = GRRasterScene() 
    hash = scene.prov.add_terrain("./n27_w111_1arc_v3.dted")

    #scene.add_geometry(hash)
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtWidgets.QApplication.instance().exec_()




