import provider
import scene

if __name__ == '__main__':
    gscene = scene.GRRasterScene() 
    terrain = provider.RasterTerrain("../data/n37_w107_1arc_v3.tif", skip=16)
    terrain2 = provider.RasterTerrain("../data/n37_w108_1arc_v3.tif", skip=16)

    gscene.prov.add(terrain)
    gscene.prov.add(terrain2)
    gscene.resolve()
    gscene.show()



