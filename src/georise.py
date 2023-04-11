import provider
import scene

if __name__ == '__main__':
    gscene = scene.GRRasterScene() 
    terrain = provider.RasterTerrain("../data/n37_w107_1arc_v3.tif", skip=12)
    terrain2 = provider.RasterTerrain("../data/n37_w108_1arc_v3.tif", skip=16)
    terrain3 = provider.RasterTerrain("../data/n37_w104_1arc_v3.tif", skip=16)

    gscene.prov.add(terrain)
    gscene.prov.add(terrain2)
    gscene.prov.add(terrain3)
    gscene.resolve()
    gscene.show()



