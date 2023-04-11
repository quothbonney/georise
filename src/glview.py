import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import numpy as np

class GRWidget(gl.GLViewWidget):
    unit_clicked = QtCore.pyqtSignal(object)

    """ 
    Override GLViewWidget with enhanced behavior

    """

    def __init__(self, provider, app=None):

        gl.GLViewWidget.__init__(self, parent=app)
        self.clickable = True
        self._mouse_click_pos = QtCore.QPoint()
        self.means = {}
        self.mesh_items = self.items
        self.candidates = []
        self.provider = provider

    def resolve_borders(self):  
      for key in self.provider.data:
        min_ll = self.provider.data[key]['coord_pos']
        max_ll = self.provider.data[key]['coord_max']
        arr = self.provider.data[key]['g_array']
        shapey, shapex = arr.shape
        zscale = self.provider.data[key]['mesh_scale'][2]
        point1 = (min_ll[0], min_ll[1], arr[0, 0] * zscale)
        point2 = (max_ll[0], min_ll[1], arr[shapey - 1, 0] * zscale)
        point3 = (min_ll[0], max_ll[1], arr[0, shapex - 1] * zscale)
        point4 = (max_ll[0], max_ll[1], arr[shapey-1, shapex-1] * zscale)
        print(point1, point2)
        line1 = gl.GLLinePlotItem(pos=np.array([point1, point2]), color=(1, 0, 0, 1), width=1, antialias=True)
        line2 = gl.GLLinePlotItem(pos=np.array([point2, point4]), color=(1, 0, 0, 1), width=1, antialias=True)
        line3 = gl.GLLinePlotItem(pos=np.array([point4, point3]), color=(1, 0, 0, 1), width=1, antialias=True)
        line4 = gl.GLLinePlotItem(pos=np.array([point3, point1]), color=(1, 0, 0, 1), width=1, antialias=True)

        self.addItem(line1)
        self.addItem(line2)
        self.addItem(line3)
        self.addItem(line4)

    def resolve(self):
      for key in self.provider.data:
        if self.provider.data[key]['border']:
            self.resolve_borders()
        self.addItem(self.provider.data[key]['mesh'])


    def set_provider(self, prov):
        self.prov = prov


    def set_means(self, means):
        self.means = means

    def set_clickable(self, choice):
        self.clickable = choice

    def mousePressEvent(self, ev):
        """ Store the position of the mouse press for later use.

        """
        gl.GLViewWidget.mousePressEvent(self, ev)
        self._mouse_click_pos = self.mousePos
        pos = self._mouse_click_pos 

        
            # Calculate ray origin and direction
        ray_origin = self.cameraPosition()
        ray_ndc = np.array([pos.x() / self.width() * 2 - 1, 1 - pos.y() / self.height() * 2, 0, 1])
        view_mat_inv = np.linalg.inv(np.array(self.viewMatrix().data()).reshape((4,4)))
        proj_mat_inv = np.linalg.inv(np.array(self.projectionMatrix().data()).reshape((4,4)))
        ray_clip = np.dot(proj_mat_inv, ray_ndc)
        ray_world = np.dot(view_mat_inv, ray_clip)
        ray_direction = (ray_world[:3] / ray_world[3] - ray_origin)
        ray_direction /= np.linalg.norm(ray_direction)

        


    def mouseReleaseEvent(self, ev):
        """ Allow for single click to move and right click for context menu.

        Also emits a sigUpdate to refresh listeners.
        """
        gl.GLViewWidget.mouseReleaseEvent(self, ev)
        if self._mouse_click_pos == ev.pos() and self.clickable:
            if ev.button() == 1:
                self.mouse_position()
        self._prev_zoom_pos = None
        self._prev_pan_pos = None

    def mouse_position(self):
        pass
