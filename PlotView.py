from PySide6.QtGui import QPainter, QBrush, QColor, QImage, QPixmap, QPen, QMouseEvent
from PySide6.QtQml import QmlElement
from PySide6.QtCore import Signal, Slot
from PySide6.QtQuick import QQuickPaintedItem

# import numpy as np
# import cv2

QML_IMPORT_NAME = "PlotView"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0  # Optional

ENABLE_DEBUG = True

@QmlElement
class PlotView(QQuickPaintedItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap = None
        self._current_image = None

    @Slot()
    def handleResize(self):
        if not self._pixmap:
            return
        self._pixmap = QPixmap.fromImage(self._current_image.scaled(int(self.width()), int(self.height())))
        self.update()

    @Slot(QImage, result=None)
    def setPlot(self, image: QImage):
        if not image:
            return
        if ENABLE_DEBUG:
            print (f"setPlot to {image.width()}x{image.height()}")
            image.save("plot.png", "PNG")
        self._current_image = image
        self.scale_x = self.width() * 1.0 / image.width()
        self.scale_y = self.height() * 1.0 / image.height()
        self._pixmap = QPixmap.fromImage(
            image.scaled(int(self.width()), int(self.height())))
        self.update()

    def paint(self, painter: QPainter):
        # draw the court lines
        if self._pixmap is not None:
            painter.drawPixmap(0, 0, self._pixmap)
        

