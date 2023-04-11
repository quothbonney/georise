import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import matplotlib.pyplot as plt
from typing import Tuple
import numpy as np
import sys
import provider, util
from glview import GRWidget


class SceneCoordinateProvider:
    def __init__(self) -> None:
        self.__ll_origin = (0, 0, 0)
        self.__origin_scaling = (1, 1, 1)
        self.__spatial_scaling = (1, 1, 1)

    def set_origin_ll(self, transform):
        self.__ll_origin = (transform.yo, transform.xo, 0)
        self.__spatial_scaling = (transform.nsres, transform.weres, 1/transform.get_size_meters()[0])

        max_ll = (transform.yo + (transform.nsres * transform.ysz), transform.xo + (transform.weres * transform.xsz))

        lon_dist = util.get_distance_between_lat_lon_points_geopy(self.__ll_origin[0], self.__ll_origin[1], self.__ll_origin[0], max_ll[1])
        lat_dist = util.get_distance_between_lat_lon_points_geopy(self.__ll_origin[0], self.__ll_origin[1], max_ll[0], self.__ll_origin[1])

        self.__origin_scaling= tuple((lat_dist / lat_dist, lon_dist / lat_dist, 1))
      
    def get_origin(self):
        return self.__ll_origin

    def get_scaling(self):
        adjusted_scaling = tuple((spacial*coordinate for spacial, coordinate in zip(self.__spatial_scaling, self.__origin_scaling)))
        return adjusted_scaling
     
    # Returns the top left and bottom right coordinates for the raster
    def get_position_from_transform(self, transform): 
        dist = (transform.yo - self.__ll_origin[0], transform.xo - self.__ll_origin[1], 0) 
        max_vals = (transform.yo + (transform.nsres * transform.ysz), transform.xo + (transform.weres * transform.xsz))
        max_dist = (max_vals[0] - self.__ll_origin[0], max_vals[1] - self.__ll_origin[1], 0) 
        # Top left location
        tl = (dist[0] * self.__origin_scaling[0], dist[1] * self.__origin_scaling[1], 0)
        br = (max_dist[0] * self.__origin_scaling[0], max_dist[1] * self.__origin_scaling[1], 0)
        
        return (tl, br) 



class GRRasterScene:
    app = QtWidgets.QApplication([])
    prov = provider.GRDataProvider()
    w = GRWidget(prov)

    def __init__(self) -> None: 
        self.w.set_means(self.prov.data)
        self.w.opts['distance'] = 10 
        self.w.setWindowTitle('Georise Visual')
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
        coord_prov = SceneCoordinateProvider()
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

            if key == 0:
                coord_prov.set_origin_ll(hashed["transform"])
            
            surf = gl.GLSurfacePlotItem(x=y, y=x, z=elevs, colors=img, shader='shaded')

            scaling = coord_prov.get_scaling()
            hashed['coord_pos'], hashed['coord_max'] = coord_prov.get_position_from_transform(hashed['transform'])
            hashed['mesh_scale'] = (scaling[0] * skip, scaling[1] * skip, scaling[2])

            surf.translate(*hashed['coord_pos'])
            surf.scale(*hashed['mesh_scale'])
            # surf.translate(hashed['transform'].yo, hashed['transform'].xo, 0)

            surf.setGLOptions('opaque')
            surf.setDepthValue(0)

            self.prov.data[key]['mesh'] = surf

        self.w.set_provider(self.prov)
        self.w.resolve()
