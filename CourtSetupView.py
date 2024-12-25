
from PySide6.QtGui import QPainter, QBrush, QColor, QImage, QPixmap, QPen, QMouseEvent
from PySide6.QtQml import QmlElement
from PySide6.QtCore import Signal, Slot
from PySide6.QtQuick import QQuickPaintedItem

import numpy as np
import cv2


QML_IMPORT_NAME = "CourtSetupView"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0  # Optional

@QmlElement
class CourtSetupView(QQuickPaintedItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._ref2img_homography = np.matrix(np.eye(3))

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
        self._pixmap = None
        self._draw_court = self._court_reference.copy() 
        self._draw_court["baseline_top"] =np.asarray ([(50, 10), (100, 10)])
        self._draw_court["baseline_bottom"] =np.asarray ([(30, 100), (120, 100)])
        self._selected_points = []
        self._points_for_update_homography = set()
        self._img2ref_homography = np.matrix(np.eye(3))
        self.find_initial_homography()

        # print courtsetjupview size
        print(f"courtsetupview size: {self.width()}, {self.height()}")

    def find_initial_homography(self):
        dstPoints = np.array([*self._draw_court["baseline_top"], *self._draw_court["baseline_bottom"]], dtype=np.float32)
        srcPoints = np.array([*self._court_reference["baseline_top"], *self._court_reference["baseline_bottom"]], dtype=np.float32)
        self._ref2img_homography,  _ = cv2.findHomography(srcPoints, dstPoints, method=0) 
        self._img2ref_homography = cv2.invert(self._ref2img_homography)[1]
        print("homography", self._ref2img_homography)

        for key in self._draw_court:
            in_point = np.array([*self._court_reference[key]], dtype=np.float32).reshape(-1, 1, 2) 
            self._draw_court[key] = np.int32(cv2.perspectiveTransform(in_point, self._ref2img_homography).reshape(-1, 2))



    @Slot(QImage, result=None)
    def setImage(self, image: QImage):
        if not image:
            return
        self._pixmap = QPixmap.fromImage(
            image.scaled(int(self.width()), int(self.height())))
        self.update()

    @Slot(float, float)
    def handleMousePressed(self, mouse_x, mouse_y):
        print(f"Mouse pressed at {mouse_x}, {mouse_y}")
        for key in self._draw_court:
            point1 = self._draw_court[key][0]
            point2 = self._draw_court[key][1]

            if np.linalg.norm(np.array(point1) - np.array([mouse_x, mouse_y])) < 5:
                print(f"Selected {key} point 1")
                self._selected_points.append(key + "-0") 
            elif np.linalg.norm(np.array(point2) - np.array([mouse_x, mouse_y])) < 5:
                print(f"Selected {key} point 2")
                self._selected_points.append(key + "-1")
                
    @Slot(float, float)
    def handleRightClicked(self, mouse_x, mouse_y):
        print(f"Right Mouse pressed at {mouse_x}, {mouse_y}")
        for key in self._draw_court:
            point1 = self._draw_court[key][0]
            point2 = self._draw_court[key][1]

            if np.linalg.norm(np.array(point1) - np.array([mouse_x, mouse_y])) < 5:
                print(f"Selected {key} point 1")
                self._points_for_update_homography.add(key + "-0") 
                break
            elif np.linalg.norm(np.array(point2) - np.array([mouse_x, mouse_y])) < 5:
                print(f"Selected {key} point 2")
                self._points_for_update_homography.add(key + "-1")
                break

        self.update()

    @Slot(float, float)
    def handleMouseReleased(self, mouse_x, mouse_y):
        print(f"Mouse released at {mouse_x}, {mouse_y}")
        self._selected_points = []

    @Slot(float, float)
    def handleMouseMoved(self, mouse_x, mouse_y):
        if self._selected_points:
            for selected_point in self._selected_points:
                key, point = selected_point.split("-")
                point = int(point)
                self._draw_court[key][point] = [mouse_x, mouse_y]
                self.update()

    @Slot()
    def update_homography(self):
        if len(self._points_for_update_homography) >= 4:
            dstPoints = []
            srcPoints = []
            for point in self._points_for_update_homography:
                key, point = point.split("-")
                point = int(point)
                dstPoints.append(self._draw_court[key][point])
                srcPoints.append(self._court_reference[key][point])
            dstPoints = np.array(dstPoints, dtype=np.float32)
            srcPoints = np.array(srcPoints, dtype=np.float32)
            self._ref2img_homography,  _ = cv2.findHomography(srcPoints, dstPoints, method=0) 
            self._img2ref_homography = cv2.invert(self._ref2img_homography)[1]
            print("homography", self._ref2img_homography)
            self._points_for_update_homography = set()

            # update all draw court points
            for key in self._draw_court:
                in_point = np.array([*self._court_reference[key]], dtype=np.float32).reshape(-1, 1, 2) 
                self._draw_court[key] = np.int32(cv2.perspectiveTransform(in_point, self._ref2img_homography).reshape(-1, 2))

            self.update()

    def paint(self, painter: QPainter):
        
        # draw the court lines
        if self._pixmap is not None:
            painter.drawPixmap(0, 0, self._pixmap)
        
        # Set the brush for the fill color
        # painter.setBrush(QColor(200, 150, 255))  # Light purple

        # Set the pen for the border
        pen = QPen(QColor(100, 100, 255), 4)  # Blue border with width 4
        painter.setPen(pen)

        # Draw a rectangle that fills the item
        #rect = self.boundingRect()
        #painter.drawRect(rect.adjusted(10, 10, -10, -10))  # Add padding

        painter.drawLine(*self._draw_court["baseline_top"][0], *self._draw_court["baseline_top"][1])
        painter.drawLine(*self._draw_court["baseline_bottom"][0], *self._draw_court["baseline_bottom"][1])
        painter.drawLine(*self._draw_court["net"][0], *self._draw_court["net"][1])
        painter.drawLine(*self._draw_court["left_court_line"][0], *self._draw_court["left_court_line"][1])
        painter.drawLine(*self._draw_court["right_court_line"][0], *self._draw_court["right_court_line"][1])
        painter.drawLine(*self._draw_court["top_inner_line"][0], *self._draw_court["top_inner_line"][1])
        painter.drawLine(*self._draw_court["bottom_inner_line"][0], *self._draw_court["bottom_inner_line"][1])
        painter.drawLine(*self._draw_court["top_middle_line"][0], *self._draw_court["top_middle_line"][1])
        painter.drawLine(*self._draw_court["bottom_middle_line"][0], *self._draw_court["bottom_middle_line"][1])
        # draw the court reference

        # draw the points for update homography
        for point in self._points_for_update_homography:
            key, point = point.split("-")
            point = int(point)
            painter.setBrush(QColor(255, 0, 0))
            pen = QPen(QColor(255, 0, 255), 2)  # Blue border with width 4
            painter.setPen(pen)
            
            



