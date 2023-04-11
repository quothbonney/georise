from osgeo import gdal
from transform import TerrainTransform

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
        self.__data['coord_pos'] = None 
        self.__data['coord_max'] = None
        self.__data['mesh_scale'] = (1, 1, 1)
        self.__data['border'] = True

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
