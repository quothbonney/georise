from osgeo import gdal
import numpy as np
from .transform import TerrainTransform

class RasterTerrain:
    def __init__(self, fname: str, **kwargs) -> None:
        self.__data = {} 
        self.fname = fname
        src = gdal.Open(fname, gdal.GA_ReadOnly)
        band = src.GetRasterBand(1)
        if not band:
            raise ValueError(f"No data in raster band {fname}")
        geo_transform = src.GetGeoTransform() 
        transform_object = TerrainTransform(geo_transform, src.RasterXSize, src.RasterYSize)


        geotiff_unit_type = band.GetUnitType()
        elevation_data = band.ReadAsArray()

        # Store minimum and maximum values for cmap testing
        # (Passed to the provider object when added to scene)
        self.minz = np.min(elevation_data)
        self.maxz = np.max(elevation_data)

        # Convert the raster to meters if it is another data type. Not tested.
        if geotiff_unit_type == 'ft' or geotiff_unit_type == 'feet':
            elevation_data = elevation_data * 0.3048  # Convert feet to meters
        elif geotiff_unit_type == 'yd' or geotiff_unit_type == 'yards':
            elevation_data = elevation_data * 0.9144  # Convert yards to meters

        self.__data['transform'] = transform_object
        self.__data['g_array'] = elevation_data
        self.__data['driver'] = src.GetDriver().ShortName
        self.__data['coord_pos'] = None 
        self.__data['coord_max'] = None
        self.__data['mesh_scale'] = (1, 1, 1)
        self.__data['border'] = True

        # If the transform object is not valid, add dummy data
        if not transform_object.validate_transform():
            print(f"WARNING: Geolocation data from file {self.fname}. cannot be read. GeoTransform returned  {transform_object.get()}. This most likely is due to corrupted metadata. If the problem persists, consider RasterTerrain.add_metadata()")
            self.add_metadata()

        print(self.__data['transform'])
        for key, value in kwargs.items():
            setattr(self, key, value)
            self.__data[key] = value

    def get_data(self):
        return self.__data;

    def set_scale(self, x=None, y=None, z=None):
        list_tup = list(self.__data['mesh_scale'])
        if x:
            list_tup[0] = x
            self.__data['mesh_scale'] = tuple(list_tup)
        if y:
            list_tup[1] = y 
            self.__data['mesh_scale'] = tuple(list_tup)
        if z:
            list_tup[2] = z 
            self.__data['mesh_scale'] = tuple(list_tup)

    def add_metadata(self, lonorigin=0, latorigin=0, nsres=-0.001, weres=-0.001, arc=None):
        if arc:
            self.__data['transform'].nsres = arc[0]
            self.__data['transform'].weres = arc[1] 
        else:
            self.__data['transform'].nsres = nsres 
            self.__data['transform'].weres = weres 
        self.__data['transform'].yo = lonorigin
        self.__data['transform'].xo = latorigin 
