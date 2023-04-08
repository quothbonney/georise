import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import matplotlib.pyplot as plt
from typing import Tuple
import numpy as np
import sys
import provider, util

class GRRasterScene:
    app = QtWidgets.QApplication([])
    w = gl.GLViewWidget()
    prov = provider.GRDataProvider()
    scaling = (1, 1, 1)

    def __init__(self) -> None: 
        self.w.opts['distance'] = 10 
        self.w.setWindowTitle('pyqtgraph example: GLLinePlotItem')
        self.w.setGeometry(0, 0, 600, 600)

    def show(self) -> None:
        print("Loading terrains... This may take a moment")
        self.w.show()
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtWidgets.QApplication.instance().exec_()

    def get_origin_from_minimum(self) -> Tuple[float, float]:
        # Set to the maxium values for each
        lat_min = -90.0
        lon_min = 90.0
        for key in self.prov.data:
            if self.prov.data[key]['transform'].yo > lat_min:
                lat_min = self.prov.data[key]['transform'].yo
            if self.prov.data[key]['transform'].xo < lon_min:
                lon_min = self.prov.data[key]['transform'].xo
        
        print(lat_min, lon_min)
        return (lat_min, lon_min)

    def get_position(self, transform, scale: Tuple[float, float, float]) -> Tuple[int, int]:
        lat1, lon1 = self.ll_origin
        lat2, lon2 = (transform.yo, transform.xo)

        lat_ind = (lat2-lat1)
        lon_ind = (lon2-lon1)
        # lat_dist = get_distance_between_lat_lon_points_geopy(lat1, lon1, lat2, lon1)
        # lon_dist = get_distance_between_lat_lon_points_geopy(lat1, lon1, lat1, lon2)

        # lat_ind = int(lat_dist / (scale[1]*transform.ysz))
        # lon_ind = int(lon_dist / (scale[0]*transform.xsz))

        return (lat_ind, lon_ind)
    
    def resolve(self):
        self.ll_origin = self.get_origin_from_minimum()
        for key in self.prov.data.keys():

            hashed = self.prov.data[key]
            skip = hashed.get('skip', 4)


            elevs = hashed["g_array"][::skip, ::skip]

            # arr = data_tup[1]
            x_sz, y_sz = elevs.shape

            y = np.linspace(0, y_sz - 1, y_sz)
            x = np.linspace(0, x_sz - 1, x_sz)

            cmap = plt.get_cmap('twilight_shifted_r')
            minZ=np.min(elevs)
            maxZ=np.max(elevs)
            img = cmap((elevs-minZ)/(maxZ -minZ))
            
            surf = gl.GLSurfacePlotItem(x=y, y=x, z=elevs, colors = img, shader='shaded')
            
            # Let the first raster define the scaling (temporary placement solution)
            if key == 0:
                ob = self.prov.data[key]["transform"]
                raster_distance = util.get_distance_between_lat_lon_points_geopy(*self.ll_origin, ob.yo + (ob.nsres * ob.ysz), self.ll_origin[1])
                self.scaling = (ob.nsres, ob.weres, 1/raster_distance) 


            position: Tuple[float, float] = self.get_position(hashed['transform'], self.scaling)

            print("SCALE", self.scaling)
            print("POSITION", position)

            surf.translate(*position, 0)

            surf.scale(self.scaling[0] * skip, self.scaling[1] * skip, self.scaling[2])
            surf.translate(*hashed['coord_pos'])

            surf.setGLOptions('opaque')
            surf.setDepthValue(0)

            self.w.addItem(surf)