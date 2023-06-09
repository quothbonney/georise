import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QVBoxLayout
import matplotlib.pyplot as plt
from typing import Tuple
import numpy as np
import sys
from . import provider, util, raster
from .glview import GRWidget
from .raster import RasterTerrain

class GRRasterScene:
    app = QtWidgets.QApplication([])
    prov = provider.GRDataProvider()
    w = GRWidget(prov)

    # Aliasing functions to prettify the API
    add = prov.add

    def __init__(self) -> None: 
        self.w.set_means(self.prov.data)
        self.w.opts['distance'] = 10 
        self.w.setWindowTitle('Georise Visual')
        self.w.setGeometry(0, 0, 600, 600)
        self.resolved = False

        # self.scale_overlay = ScaleOverlay(self.w)
        # self.scale_overlay.setGeometry(10, 10, 200, 100)

    def raster(self, fname, **kwargs):
        terrain = raster.RasterTerrain(fname=fname, **kwargs)
        self.prov.add(terrain)
        
    def update_scale_overlay(self):
        # Get the current zoom factor from the camera
        zoom_factor = self.w.opts['distance']
        # Scale the rectangle accordingly
        scale_factor = 1 / zoom_factor
        self.scale_overlay.update_scale(scale_factor)

    def show(self) -> None:
        print("Loading terrains... This may take a moment")
        if not self.resolved:
            self.resolve()
        self.w.show()
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtWidgets.QApplication.instance().exec_()

    def get_origin_from_minimum(self) -> Tuple[float, float]:
        # Set to the maxium values for each

        lat_min = -90.0
        lon_min = 90.0
        for key in self.prov.data:
            if (
                self.prov.data[key].transform.yo < -90 or 
                self.prov.data[key].transform.yo > 90 or 
                self.prov.data[key].transform.xo < -90 or 
                self.prov.data[key].transform.xo > 90
                ):
                return (0, 0)

            if self.prov.data[key].transform.yo > lat_min:
                lat_min = self.prov.data[key].transform.yo
            if self.prov.data[key].transform.xo < lon_min:
                lon_min = self.prov.data[key].transform.xo
        
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

            hashed: RasterTerrain = self.prov.data[key]
            skip = hashed.skip


            elevs = hashed.g_array[::skip, ::skip]

            # arr = data_tup[1]
            x_sz, y_sz = elevs.shape
            m_sz = max(x_sz, y_sz)

            y = np.linspace(0, y_sz - 1, y_sz)
            x = np.linspace(0, x_sz - 1, x_sz)

            cmap = plt.get_cmap(self.prov.cmap)
            minZ, maxZ = self.prov.z_interval
            img = cmap((elevs-minZ)/(maxZ -minZ))

            if key == 0 and hashed.transform:
                self.prov.coord.set_origin_ll(hashed.transform)

            scaling = self.prov.coord.get_scaling()
            hashed.coord_pos, hashed.coord_max = self.prov.coord.get_position_from_transform(hashed.transform)
            hashed.mesh_scale = (scaling[0] * skip, scaling[1] * skip, scaling[2])

            # AWFUL CODE WARNING: The way this whole thing works is with dictoaries
            # That hold all the values. This works pretty well. the problem is that when
            # You put all the attributes into a seperate dictionary, you lose all of the methods
            # Attached to them. Now, at the peril of refactoring this whole codebase, I am passing
            # The mesh constructor function `construct_rasters` as a first class object to the
            # Dictionary. I apologize.
            hashed.construct_rasters(x=x, y=y, z=elevs, colors=img)

        self.w.set_provider(self.prov)
        self.w.resolve()
        self.resolved = True
