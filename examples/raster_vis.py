# This is the simplest way of creating a 3D scene with Georise
# It is designed to be as similar to matplotlib as possible for ease of use

import georise.scene

if __name__ == '__main__':
    # Instantiate the scene
    gplt = georise.scene.GRRasterScene() 

    # Add terrains from filepath (use skip to save on memory)
    # terrain = RasterTerrain("../data/n37_w107_1arc_v3.tif", skip=16)
    # terrain2 = RasterTerrain("../data/n37_w104_1arc_v3.tif", skip=16)

    gplt.raster("../data/n37_w107_1arc_v3.tif", skip=2)
    gplt.raster("../data/n37_w108_1arc_v3.tif", skip=2)
    # Add terrains as *args and show
    # gplt.add(terrain, terrain2)
    gplt.show()



