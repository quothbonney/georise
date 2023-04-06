import pyqtgraph as pg
import pyqtgraph.opengl as gl
from osgeo import gdal, osr, ogr
import numpy as np
import sys
import matplotlib.pyplot as plt
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from typing import Tuple

class TerrainTransform:
    xo, yo, xres, yres, colrot, rowrot, weres, nsres, xsz, ysz = [None for _ in range(10)]

    def __init__(self, geo_transform: Tuple[float, ...], _xsz: int, _ysz: int) -> None:
        self.xo, self.weres, self.rowrot, self.yo, self.colrot, self.yres = geo_transform
        self.xsz = _xsz;
        self.ysz = _ysz;

    def get(self):
        return (self.xo, self.weres, self.rowrot, self.yo, self.colrot, self.yres, self.xsz, self.ysz)
        

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
        tup = (src.GetGeoTransform(), band.ReadAsArray())

        self.data[self.__hash] = tup

        print(self.data)

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
    hash = scene.prov.add_terrain("./512.tif")

    scene.add_geometry(hash)
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtWidgets.QApplication.instance().exec_()




