
from PySide6.QtGui import QPainter, QBrush, QColor, QImage, QPixmap, QPen
from PySide6.QtQml import QmlElement
from PySide6.QtCore import Signal, Slot
from PySide6.QtQuick import QQuickPaintedItem, QQuickView

import numpy as np
import cv2


QML_IMPORT_NAME = "CourtSetupView"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0  # Optional

@QmlElement
class CourtSetupView(QQuickPaintedItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._homography = np.matrix(np.eye(3))

        self._court_reference = {
            "baseline_top" : np.asarray([(286, 561), (896, 561)]),
            "baseline_bottom" :np.asarray ([(286, 1902), (896, 1902)]),
            "net" :np.asarray ([(286, 1171), (896, 1171)]),
            "left_court_line" :np.asarray ([(286, 561), (286, 1902)]),
            "right_court_line" :np.asarray ([(896, 561), (896, 1902)]),
            "top_inner_line" :np.asarray ([(286, 1018), (896, 1018)]),
            "bottom_inner_line" :np.asarray ([(286, 1445), (896, 1445)]),
            "top_middle_line" :np.asarray ([(591, 561), (591, 1018)]),
            "bottom_middle_line" :np.asarray ([(591, 1445), (591, 1902)]),
        }
        self._draw_court = self._court_reference.copy() 
        self._draw_court["baseline_top"] =np.asarray ([(50, 10), (100, 10)])
        self._draw_court["baseline_bottom"] =np.asarray ([(30, 100), (120, 100)])

        self._pixmap = None
        # print courtsetjupview size
        print(f"courtsetupview size: {self.width()}, {self.height()}")

    def find_initial_homography(self):
        srcPoints = np.array([*self._draw_court["baseline_top"], *self._draw_court["baseline_bottom"]], dtype=np.float32)
        dstPoints = np.array([*self._court_reference["baseline_top"], *self._court_reference["baseline_bottom"]], dtype=np.float32)
        self._homography = cv2.findHomography(srcPoints, dstPoints, cv2.RANSAC, 5.0)

        for key in self._draw_court:
            self._draw_court[key] = cv2.perspectiveTransform(np.array([self._court_reference[key]], dtype=np.float32), self._homography)[0]



        # update the court reference

    @Slot(QImage, result=None)
    def setImage(self, image: QImage):
        if not image:
            return
        self._pixmap = QPixmap.fromImage(
            image.scaled(int(self.width()), int(self.height())))
        self.update()

    def paint(self, painter: QPainter):
        
        if not self._pixmap:
            return
        painter.drawPixmap(0, 0, self._pixmap)
        # draw the court lines
        
        #pen = QPen()
        #pen.setColor(QColor("#007430"))
        #pen.setWidth(2)
        #painter.setPen(pen)

        #painter.drawLine(*self._court_reference.baseline_top[0], *self._court_reference.baseline_top[1])
        #painter.drawLine(*self._court_reference.baseline_bottom[0], *self._court_reference.baseline_bottom[1])
        #painter.drawLine(*self._court_reference.net[0], *self._court_reference.net[1])
        #painter.drawLine(*self._court_reference.top_inner_line[0], *self._court_reference.top_inner_line[1])
        #painter.drawLine(*self._court_reference.bottom_inner_line[0], *self._court_reference.bottom_inner_line[1])
        #painter.drawLine(*self._court_reference.left_court_line[0], *self._court_reference.left_court_line[1])
        #painter.drawLine(*self._court_reference.right_court_line[0], *self._court_reference.right_court_line[1])
        #painter.drawLine(*self._court_reference.top_middle_line[0], *self._court_reference.top_middle_line[1])
        
        # draw the court reference
