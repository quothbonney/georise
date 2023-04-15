from . import provider
from . import scene
from .raster import RasterTerrain
import constants

if __name__ == '__main__':
    gscene = scene.GRRasterScene() 
    # terrain = provider.RasterTerrain("../data/ldco48i0100a.tif", skip=100)
    # terrain = provider.RasterTerrain("../data/IPR201411181602513544N09769W.TIF", skip=4)
    # terrain.set_scale(z=0.004 )
    terrain3 = RasterTerrain("../data/n37_w107_1arc_v3.tif", skip=16)
    # terrain512 = provider.RasterTerrain("../data/512.tif", skip=16)
    # terrain512.add_metadata(latorigin=-108, lonorigin=38, arc=constants.ONE_ARC_SEC)

    gscene.prov.add(terrain3)
    gscene.resolve()
    gscene.show()



