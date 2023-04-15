from PyQt5.QtWidgets import QGraphicsRectItem
from PyQt5.QtCore import Qt
import pyqtgraph as pg

class ScaleOverlay(pg.GraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set widget style
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        #self.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)

        # Set up the GraphicsScene
        self.graphics_scene = pg.GraphicsScene()
        self.setScene(self.graphics_scene)

        # Add rectangle item
        self.rectangle = QGraphicsRectItem(0, 0, 100, 20)
        self.rectangle.setBrush(pg.mkBrush('w'))
        self.rectangle.setOpacity(0.7)
        self.graphics_scene.addItem(self.rectangle)

    def update_scale(self, scale_factor):
        self.rectangle.setRect(0, 0, 100 * scale_factor, 20 * scale_factor)