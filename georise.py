import pyqtgraph as pg
import pyqtgraph.opengl as gl
from osgeo import gdal
import numpy as np
import sys
import matplotlib.pyplot as plt
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets

gl.shaders.Shaders.append(gl.shaders.ShaderProgram('myShader2', [
    gl.shaders.VertexShader("""
            varying vec3 normal;
            varying float height;
            void main() {
                // compute here for use in fragment shader
                normal = normalize(gl_NormalMatrix * gl_Normal);
                height = gl_Vertex.z;
                gl_FrontColor = gl_Color;
                gl_BackColor = gl_Color;
                gl_Position = ftransform();
            }
        """),
    gl.shaders.FragmentShader("""
            varying vec3 normal;
            varying float height;
            void main() {
                // Map height to a color gradient
                vec4 color;
                float minHeight = 0.0;
                float maxHeight = 1.0;
                float normalizedHeight = (height - minHeight) / (maxHeight - minHeight);

                color.r = mix(0.2, 0.8, normalizedHeight); // red component
                color.g = mix(0.5, 1.0, normalizedHeight); // green component
                color.b = mix(0.0, 0.3, normalizedHeight); // blue component
                color.a = 1.0; // alpha component

                gl_FragColor = color;
            }
        """)
]))

gl.shaders.Shaders.append(gl.shaders.ShaderProgram('myShader', [
    gl.shaders.VertexShader("""
            varying vec3 normal;
            void main() {
                // compute here for use in fragment shader
                normal = normalize(gl_NormalMatrix * gl_Normal);
                gl_FrontColor = gl_Color;
                gl_BackColor = gl_Color;
                gl_Position = ftransform();
            }
        """),
    gl.shaders.FragmentShader("""
            varying vec3 normal;
            void main() {
                vec4 color = gl_Color;
                color.x = 0.0;
                color.y = (normal.y + 1.0) * 0.5;
                color.z = 0.0;
                gl_FragColor = color;
            }
        """)
]))

class GRDataProvider:
    data = {}
    __hash = 0

    @classmethod
    def increment_hash(cls):
       cls.__hash += 1 

    def add_terrain(self, fname: str) -> int:
        src = gdal.Open(fname, gdal.GA_ReadOnly)
        band = src.GetRasterBand(1)
        if not band:
            raise ValueError(f"No data in raster band {fname}")
        tup = (src.GetGeoTransform(), band.ReadAsArray())

        self.data[self.__hash] = tup

        print(self.data)

        return self.__hash


class GRRasterScene:
    app = QtWidgets.QApplication([])
    w = gl.GLViewWidget()
    prov = GRDataProvider()

    def __init__(self) -> None: 
        self.w.opts['distance'] = 10 
        self.w.setWindowTitle('pyqtgraph example: GLLinePlotItem')
        self.w.setGeometry(0, 0, 600, 600)
        self.w.show()

    def add_geometry(self, hash):
        data_tup = self.prov.data[hash]
        # arr = data_tup[1]
        x_sz, y_sz = data_tup[1].shape

        y = np.linspace(0, y_sz - 1, y_sz)
        x = np.linspace(0, x_sz - 1, x_sz)


        cmap = plt.get_cmap('twilight_shifted_r')
        minZ=np.min(data_tup[1])
        maxZ=np.max(data_tup[1])
        img = cmap((data_tup[1]-minZ)/(maxZ -minZ))
        
        surf = gl.GLSurfacePlotItem(x=y, y=x, z=data_tup[1], colors = img, shader='shaded')

        surf.setGLOptions('opaque')
        surf.setDepthValue(0)

        self.w.addItem(surf)




if __name__ == '__main__':
    scene = GRRasterScene() 
    hash = scene.prov.add_terrain("./512.tif")

    scene.add_geometry(hash)
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtWidgets.QApplication.instance().exec_()




