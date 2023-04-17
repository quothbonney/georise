from osgeo import gdal
from .transform import TerrainTransform
from . import util

class SceneCoordinateProvider:
    def __init__(self) -> None:
        self.__ll_origin = (0, 0, 0)
        self.__origin_scaling = (1, 1, 1)
        self.__spatial_scaling = (1, 1, 1)
        self.__scaling = (1, 1, 1)

    def set_origin_ll(self, transform):
        self.__ll_origin = (transform.yo, transform.xo, 0)
        self.__spatial_scaling = (transform.nsres, transform.weres, 1/transform.get_size_meters()[0])

        max_ll = (transform.yo + (transform.nsres * transform.ysz), transform.xo + (transform.weres * transform.xsz))

        lon_dist = util.get_distance_between_lat_lon_points_geopy(self.__ll_origin[0], self.__ll_origin[1], self.__ll_origin[0], max_ll[1])
        lat_dist = util.get_distance_between_lat_lon_points_geopy(self.__ll_origin[0], self.__ll_origin[1], max_ll[0], self.__ll_origin[1])

        self.__origin_scaling= tuple((lat_dist / lat_dist, lon_dist / lat_dist, 1))
        self.__scaling = tuple((spacial*coordinate for spacial, coordinate in zip(self.__spatial_scaling, self.__origin_scaling)))
      
    def get_origin(self):
        return self.__ll_origin

    def get_scaling(self):
        return self.__scaling 
     
    # Returns the top left and bottom right coordinates for the raster
    def get_position_from_transform(self, transform): 
        dist = (transform.yo - self.__ll_origin[0], transform.xo - self.__ll_origin[1], 0) 
        max_vals = (transform.yo + (transform.nsres * transform.ysz), transform.xo + (transform.weres * transform.xsz))
        max_dist = (max_vals[0] - self.__ll_origin[0], max_vals[1] - self.__ll_origin[1], 0) 
        # Top left location
        tl = (dist[0] * self.__origin_scaling[0], dist[1] * self.__origin_scaling[1], 0)
        br = (max_dist[0] * self.__origin_scaling[0], max_dist[1] * self.__origin_scaling[1], 0)
        
        return (tl, br) 


class GRDataProvider:
    data = {}
    coord = SceneCoordinateProvider()
    borders = True
    cmap = 'terrain'
    z_interval = [2 ** 16 - 1, 0]

    __hash = 0

    @classmethod
    def increment_hash(cls):
       cls.__hash += 1 


    def add(self, *terrains) -> None:
        for terrain in terrains:
            self.data[self.__hash] = terrain
            if terrain.minz < self.z_interval[0]: self.z_interval[0] = terrain.minz
            if terrain.maxz > self.z_interval[1]: self.z_interval[1] = terrain.maxz

            self.increment_hash()

        assert self.z_interval[0] < self.z_interval[1]


