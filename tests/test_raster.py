import os, sys
import tempfile
import numpy as np
import rasterio

#import pytest
import pytest
from ..georise.raster import RasterTerrain

def create_temp_geotiff() -> str:
    data = np.random.randint(0, 255, (3, 3), dtype=np.uint8)
    transform = rasterio.transform.from_origin(0, 0, 1, 1)

    with tempfile.NamedTemporaryFile(suffix=".tif", delete=False) as f:
        with rasterio.open(f.name, "w", driver="GTiff", height=3, width=3, count=1, dtype=np.uint8, crs="EPSG:4326", transform=transform) as dataset:
            dataset.write(data, 1)

        return f.name
    
def test_raster_terrain_init():
    temp_geotiff = create_temp_geotiff()

    terrain = RasterTerrain(temp_geotiff)
    assert terrain is not None
    assert terrain.fname == temp_geotiff

    os.remove(temp_geotiff)

def test_raster_terrain_get_data():
    temp_geotiff = create_temp_geotiff()

    terrain = RasterTerrain(temp_geotiff)
    data = terrain.get_data()

    assert isinstance(data, dict)
    assert "transform" in data
    assert "g_array" in data
    assert "driver" in data
    assert "coord_pos" in data
    assert "coord_max" in data
    assert "mesh_scale" in data
    assert "border" in data

    os.remove(temp_geotiff)

def test_raster_terrain_set_scale():
    temp_geotiff = create_temp_geotiff()

    terrain = RasterTerrain(temp_geotiff)
    terrain.set_scale(x=2, y=3, z=4)

    data = terrain.get_data()
    assert data["mesh_scale"] == (2, 3, 4)

    os.remove(temp_geotiff)

def test_raster_terrain_add_metadata():
    temp_geotiff = create_temp_geotiff()

    terrain = RasterTerrain(temp_geotiff)
    terrain.add_metadata(lonorigin=1, latorigin=2, nsres=-0.002, weres=-0.002)

    data = terrain.get_data()
    transform = data["transform"]

    assert transform.yo == 1
    assert transform.xo == 2
    assert transform.nsres == -0.002
    assert transform.weres == -0.002

    os.remove(temp_geotiff)
