from geopy.distance import geodesic
from osgeo import gdal, osr, ogr

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