import pyqtgraph as pg
import pyqtgraph.opengl as gl
from osgeo import gdal, osr, ogr
import numpy as np
import sys
import matplotlib.pyplot as plt
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from typing import Tuple
from geopy.distance import geodesic

def get_distance_between_lat_lon_points_geopy(lat1, lon1, lat2, lon2):
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)
    distance = geodesic(point1, point2).meters
    return distance

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


class RasterTerrain:
    def __init__(self, fname: str, **kwargs) -> None:
        self.__data = {} 
        src = gdal.Open(fname, gdal.GA_ReadOnly)
        band = src.GetRasterBand(1)
        if not band:
            raise ValueError(f"No data in raster band {fname}")

        geo_transform = src.GetGeoTransform() 

        transform_object = TerrainTransform(geo_transform, src.RasterXSize, src.RasterYSize)
        self.__data['transform'] = transform_object
        self.__data['g_array'] = band.ReadAsArray()
        self.__data['driver'] = src.GetDriver().ShortName
        self.__data['coord_pos'] = (0., 0., 0.);

        for key, value in kwargs.items():
            setattr(self, key, value)
            self.__data[key] = value

    def get_data(self):
        return self.__data;

        

class GRDataProvider:
    data = {}
    __hash = 0
    ll_origin = (0, 0)

    @classmethod
    def increment_hash(cls):
       cls.__hash += 1 


    def add(self, terrain) -> int:
        self.data[self.__hash] = terrain.get_data()
        self.increment_hash()
        return self.__hash

class GRRasterScene:
    app = QtWidgets.QApplication([])
    w = gl.GLViewWidget()
    prov = GRDataProvider()

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

        lat_dist = get_distance_between_lat_lon_points_geopy(lat1, lon1, lat2, lon1)
        lon_dist = get_distance_between_lat_lon_points_geopy(lat1, lon1, lat1, lon2)

        lat_ind = int(lat_dist / scale[1])
        lon_ind = int(lon_dist / scale[0])

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

            scale: Tuple[float, float, float] = self.prov.data[key]["transform"].get_scale()
            position: Tuple[float, float] = self.get_position(hashed['transform'], scale)

            print("SCALE", scale)
            print("POSITION", position)

            surf.translate(*position, 0)

            surf.scale(scale[0] * skip, scale[1] * skip, skip)
            surf.translate(*hashed['coord_pos'])

            surf.setGLOptions('opaque')
            surf.setDepthValue(0)

            self.w.addItem(surf)




if __name__ == '__main__':
    scene = GRRasterScene() 
    terrain = RasterTerrain("../data/n37_w107_1arc_v3.tif", skip=16)
    terrain2 = RasterTerrain("../data/n37_w104_1arc_v3.tif", skip=16)

    scene.prov.add(terrain)
    scene.prov.add(terrain2)
    scene.resolve()
    scene.show()



