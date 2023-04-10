import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import numpy as np

class GRWidget(gl.GLViewWidget):
    unit_clicked = QtCore.pyqtSignal(object)

    """ 
    Override GLViewWidget with enhanced behavior

    """

    def __init__(self, app=None):

        gl.GLViewWidget.__init__(self, parent=app)
        self.clickable = True
        self._mouse_click_pos = QtCore.QPoint()
        self.means = {}
        self.candidates = []

    def set_means(self, means):
        self.means = means

    def set_clickable(self, choice):
        self.clickable = choice

    def mousePressEvent(self, ev):
        """ Store the position of the mouse press for later use.

        """
        gl.GLViewWidget.mousePressEvent(self, ev)
        self._mouse_click_pos = self.mousePos

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
        # This function is called by a mouse event

        # Get mouse coordinates saved when the mouse is clicked( incase dragging)
        mouse_x = self._mouse_click_pos.x()
        mouse_y = self._mouse_click_pos.y()
        print(mouse_x, mouse_y)
        self.candidates = []  # Initiate a list for storing indices of picked points
        # Get height and width of 2D Viewport space
        view_w = self.width()
        view_h = self.height()
        # Convert pixel values to normalized coordinates
        x = 2.0 * mouse_x / view_w - 1.0
        y = 1.0 - (2.0 * mouse_y / view_h)
        # Convert projection and view matrix to numpy types and inverse them
        inverted_projection_matrix = self.projectionMatrix().inverted()[0]
        inverted_view_matrix = self.viewMatrix().inverted()[0]
        # Move to clip coordinates by chosing z= -1 and w 1 (Dont understand this part)
        ray_clip = QtGui.QVector4D(x, y, -1.0, 1.0)  # get transpose for matrix multiplication
        # Convert to eye space by view matrix
        ray_eye = inverted_projection_matrix * ray_clip
        ray_eye.setZ(-1)
        ray_eye.setW(0)
        # Convert to world coordinates
        ray_world = inverted_view_matrix * ray_eye
        ray_world = QtGui.QVector3D(ray_world.x(), ray_world.y(),
                                    ray_world.z())  # get transpose for matrix multiplication
        ray_world.normalize()
        print("Location0")
        # Now I 'll use the ray intersection with spheres. I assume every point is a sphere with a radius
        # Please see http://antongerdelan.net/opengl/raycasting.html scroll down to spehere intersection
        camera_position = np.array(self.cameraPosition())  # camera position should be starting point of the ray
        ray_world = np.array([ray_world.x(), ray_world.y(), ray_world.z()])
        print(ray_world)
        overlaps = []
        for key in self.means:  # Iterate over all means
            distance_to_mean = camera_position - (np.array(self.means[key]['coord_pos']) + [0, 0, 0])
            b = np.inner(ray_world, distance_to_mean)
            b = b.item(0) -0.01 ** 2
            c = np.inner(distance_to_mean, distance_to_mean)
            c = c.item(0) -0.01 ** 2
            bsqr = np.square(b)
            print(bsqr, c)
            overlap = bsqr - c
            if overlap >= 0:  # means intersection
                self.candidates.append(self.means[key])
                overlaps.append(overlap)

        if overlaps:
            winner = self.candidates[np.argmin(overlaps)]
            self.unit_clicked.emit(winner)