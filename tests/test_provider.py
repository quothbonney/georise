import pytest
from osgeo import gdal
from ..georise.transform import TerrainTransform
from ..georise import util
from ..georise.provider import SceneCoordinateProvider

def test_init():
    provider = SceneCoordinateProvider()
    assert provider.get_origin() == (0, 0, 0)
    assert provider.get_scaling() == (1, 1, 1)

def test_get_position_from_transform():
    transform1 = TerrainTransform((0, 1, 0, 0, 0, -1), 10, 10)
    transform2 = TerrainTransform((0, 1, 0, 1, 0, -1), 10, 10)
    
    provider = SceneCoordinateProvider()
    provider.set_origin_ll(transform1)
    
    # Ensure the distance between two known points is near 111 kilometers
    position = provider.get_position_from_transform(transform2)
    dist = util.get_distance_between_lat_lon_points_geopy(0, 0, 1, 0)
    assert dist == pytest.approx(111_000, 10_000)

@pytest.mark.parametrize("xo,yo,weres,nsres,xsz,ysz", [
    (0, 0, 1, -1, 10, 10),
    (0, 45, 1, -1, 10, 10),
    (0, -45, 1, -1, 10, 10),
    (0, 0, 0.01, -0.01, 100, 100),
])
def test_scaling_and_positions(xo, yo, weres, nsres, xsz, ysz):
    transform = TerrainTransform((xo, weres, 0, yo, 0, nsres), xsz, ysz)
    provider = SceneCoordinateProvider()
    provider.set_origin_ll(transform)
    scaling = provider.get_scaling()

    # Force python to give us the private attributes
    assert provider._SceneCoordinateProvider__spatial_scaling[0] == pytest.approx(nsres, rel=1e-3)
    assert provider._SceneCoordinateProvider__spatial_scaling[1] == pytest.approx(weres, rel=1e-3)
    assert provider._SceneCoordinateProvider__spatial_scaling[2] == pytest.approx(1/transform.get_size_meters()[0], rel=1e-3)

    assert provider._SceneCoordinateProvider__spatial_scaling[2] > 0.0000000000000000000000
    assert provider._SceneCoordinateProvider__spatial_scaling[2] != pytest.approx(1., rel=1e-3)



