from dataclasses import dataclass, field
from typing import List, Callable, NamedTuple, Tuple
import numpy as np
from osgeo import gdal
import pyqtgraph.opengl as gl
from .transform import TerrainTransform


class Coordinates(NamedTuple):
    x: float
    y: float
    z: float


@dataclass
class RasterTerrain:
    fname: str
    skip: int = 4
    transform: TerrainTransform = field(init=False)
    g_array: np.ndarray = field(init=False)
    driver: str = field(init=False)
    coord_pos: Coordinates = field(default_factory=lambda: Coordinates(0, 0, 0))
    coord_max: Coordinates = field(default_factory=lambda: Coordinates(0, 0, 0))
    mesh_scale: Coordinates = field(default_factory=lambda: Coordinates(1, 1, 1))
    border: bool = True
    mesh: List[gl.GLSurfacePlotItem] = field(default_factory=list)
    minz: float = field(init=False)
    maxz: float = field(init=False)

    def __post_init__(self, **kwargs) -> None:
        src = gdal.Open(self.fname, gdal.GA_ReadOnly)
        band = src.GetRasterBand(1)
        if not band:
            raise ValueError(f"No data in raster band {self.fname}")
        geo_transform = src.GetGeoTransform()

        # Create geotransform object and define attributes
        self.transform = TerrainTransform(geo_transform, src.RasterXSize, src.RasterYSize)

        geotiff_unit_type = band.GetUnitType()
        self.g_array = band.ReadAsArray()

        # Save the minimum and max z values so that the color scheme is consistent
        self.minz = np.min(self.g_array)
        self.maxz = np.max(self.g_array)

        # Attempt to convert to meters if the geotiff units are not
        if geotiff_unit_type in {'ft', 'feet'}:
            self.g_array = self.g_array * 0.3048
        elif geotiff_unit_type in {'yd', 'yards'}:
            self.g_array = self.g_array * 0.9144

        self.driver = src.GetDriver().ShortName

        if not self.transform.validate_transform():
            print(f"WARNING: Geolocation data from file {self.fname}. cannot be read. GeoTransform returned  {self.transform.get()}. This most likely is due to corrupted metadata. If the problem persists, consider RasterTerrain.add_metadata()")
            self.add_metadata()

    def set_scale(self, x: float = None, y: float = None, z: float = None) -> None:
        list_tup = list(self.mesh_scale)
        if x:
            list_tup[0] = x
            self.mesh_scale = Coordinates(*list_tup)
        if y:
            list_tup[1] = y
            self.mesh_scale = Coordinates(*list_tup)
        if z:
            list_tup[2] = z
            self.mesh_scale = Coordinates(*list_tup)

    def add_metadata(self, lonorigin: float = 0, latorigin: float = 0, nsres: float = -0.001, weres: float = -0.001, arc: Tuple[float, float] = None) -> None:
        if arc:
            self.transform.nsres = arc[0]
            self.transform.weres = arc[1]
        else:
            self.transform.nsres = nsres
            self.transform.weres = weres
        self.transform.yo = lonorigin
        self.transform.xo

    def construct_rasters(self, x, y, z, colors, **kwargs):
        surf = gl.GLSurfacePlotItem(x=x, y=y, z=z, colors=colors, shader='shaded')
        surf.translate(*self.coord_pos)
        surf.scale(*self.mesh_scale)
        # surf.translate(hashed['transform'].yo, hashed['transform'].xo, 0)

        surf.setGLOptions('opaque')
        surf.setDepthValue(0)

        self.mesh.append(surf)