import pytest
from ..georise.transform import TerrainTransform

def test_terrain_transform_init():
    geo_transform = (1, 1, 0, 1, 0, -1)
    xsz = 5
    ysz = 5

    transform = TerrainTransform(geo_transform, xsz, ysz)

    assert transform.xo == 1
    assert transform.weres == 1
    assert transform.rowrot == 0
    assert transform.yo == 1
    assert transform.colrot == 0
    assert transform.nsres == -1
    assert transform.xsz == xsz
    assert transform.ysz == ysz

def test_false_verification():
    geo_transform = (900, 0, 0, -900, 0, -1)
    xsz = 5
    ysz = 5

    transform = TerrainTransform(geo_transform, xsz, ysz)

    assert not transform.validate_transform()

def test_verification_near_border():
    geo_transform = (89.5, 0, 0, 0.002, 0, 10)
    xsz = 5
    ysz = 5

    transform = TerrainTransform(geo_transform, xsz, ysz)

    assert transform.validate_transform()

def test_false_verification_over_border():
    geo_transform = (89.5, 0, 0, 1, 0, 2000)
    xsz = 5
    ysz = 5

    transform = TerrainTransform(geo_transform, xsz, ysz)

    assert not transform.validate_transform()

def test_terrain_transform_get():
    geo_transform = (1, 1, 0, 1, 0, -1)
    xsz = 5
    ysz = 5

    transform = TerrainTransform(geo_transform, xsz, ysz)
    values = transform.get()

    assert isinstance(values, tuple)
    assert len(values) == 8
    assert values == (1, 1, 0, 1, 0, -1, xsz, ysz)

def test_terrain_transform_get_size_meters():
    geo_transform = (1, 1, 0, 1, 0, -1)
    xsz = 5
    ysz = 5

    transform = TerrainTransform(geo_transform, xsz, ysz)
    xscale, yscale = transform.get_size_meters()

    assert xscale is not None
    assert yscale is not None

def test_terrain_transform_get_scale():
    geo_transform = (1, 1, 0, 1, 0, -1)
    xsz = 5
    ysz = 5

    transform = TerrainTransform(geo_transform, xsz, ysz)
    scale = transform.get_scale()

    assert isinstance(scale, tuple)
    assert len(scale) == 3

def test_terrain_transform_validate_transform():
    geo_transform = (1, 1, 0, 1, 0, -1)
    xsz = 5
    ysz = 5

    transform = TerrainTransform(geo_transform, xsz, ysz)
    result = transform.validate_transform()

    assert result is True
