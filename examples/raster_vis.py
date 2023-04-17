# This is the simplest way of creating a 3D scene with Georise

import georise.scene

if __name__ == '__main__':
    # Instantiate the scene
    gplt = georise.scene.GRRasterScene() 

    # Add terrains from filepath (use skip to save on memory)
    # terrain = RasterTerrain("../data/n37_w107_1arc_v3.tif", skip=16)
    # terrain2 = RasterTerrain("../data/n37_w104_1arc_v3.tif", skip=16)

    gplt.raster("../data/n37_w107_1arc_v3.tif", skip=16)
    # Add terrains as *args and show
    # gplt.add(terrain, terrain2)
    gplt.show()


