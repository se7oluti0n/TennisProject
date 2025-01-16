from PySide6.QtGui import QPainter, QBrush, QColor, QImage, QPixmap, QPen, QMouseEvent
from PySide6.QtQml import QmlElement
from PySide6.QtCore import Slot
from PySide6.QtQuick import QQuickPaintedItem
import json

import numpy as np
import cv2
import os

QML_IMPORT_NAME = "CourtSetupView"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0  # Optional

@QmlElement
class CourtSetupView(QQuickPaintedItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._ref2img_homography = np.matrix(np.eye(3))

        self._court_reference_base = {
            "baseline_top" : np.asarray([(286, 561), (896, 561)]),
            "baseline_bottom" :np.asarray ([(286, 1902), (896, 1902)]),
            "net" :np.asarray ([(286, 1231), (896, 1231)]),
            "left_court_line" :np.asarray ([(286, 561), (286, 1902)]),
            "right_court_line" :np.asarray ([(896, 561), (896, 1902)]),
            "top_inner_line" :np.asarray ([(286, 1018), (896, 1018)]),
            "bottom_inner_line" :np.asarray ([(286, 1445), (896, 1445)]),
            "top_middle_line" :np.asarray ([(591, 561), (591, 1018)]),
            "bottom_middle_line" :np.asarray ([(591, 1445), (591, 1902)]),
        }


        self._court_reference = self._court_reference_base.copy()
        for key in self._court_reference:
            self._court_reference[key] = self._court_reference_base[key] - self._court_reference_base["baseline_top"][0]

        self._pixmap = None
        self._draw_court = self._court_reference.copy() 
        self._draw_court["baseline_top"] =np.asarray ([(50, 10), (100, 10)])
        self._draw_court["baseline_bottom"] =np.asarray ([(30, 100), (120, 100)])
        self._selected_points = []
        self._points_for_update_homography = set()
        self._img2ref_homography = np.matrix(np.eye(3))
        self.find_initial_homography()
        self._current_frame_id = -1
        self.ball_xy = None
        self.bounce_xy_ref = {} 

    def find_initial_homography(self):
        dstPoints = np.array([*self._draw_court["baseline_top"], *self._draw_court["baseline_bottom"]], dtype=np.float32)
        srcPoints = np.array([*self._court_reference["baseline_top"], *self._court_reference["baseline_bottom"]], dtype=np.float32)
        self._ref2img_homography,  _ = cv2.findHomography(srcPoints, dstPoints, method=0) 
        self._img2ref_homography = cv2.invert(self._ref2img_homography)[1]
        print("homography", self._ref2img_homography)

        for key in self._draw_court:
            in_point = np.array([*self._court_reference[key]], dtype=np.float32).reshape(-1, 1, 2) 
            self._draw_court[key] = np.int32(cv2.perspectiveTransform(in_point, self._ref2img_homography).reshape(-1, 2))


    @Slot()
    def handleResize(self):
        if not self._pixmap:
            return
        self._pixmap = QPixmap.fromImage(self._current_image.scaled(int(self.width()), int(self.height())))
        self.update()

    @Slot(int, QImage, result=None)
    def setImage(self, frame_id:int, image: QImage):
        if not image:
            return
        self._current_image = image
        self._current_frame_id = frame_id
        self.scale_x = self.width() * 1.0 / image.width()
        self.scale_y = self.height() * 1.0 / image.height()
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
                print(f"Update homography: Selected {key} point 1")
                self._points_for_update_homography.add(key + "-0") 
                break
            elif np.linalg.norm(np.array(point2) - np.array([mouse_x, mouse_y])) < 5:
                print(f"Update homography: Selected {key} point 1")
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
    def saveHomography(self):
        print("save homography", self._ref2img_homography)
        homography = self._ref2img_homography.tolist()
        with open("homography.json", "w") as f:
            json.dump(homography, f)


    @Slot()
    def loadHomography(self):
        if not os.path.exists("homography.json"):
            return
        with open("homography.json", "r") as f:
            homography = json.load(f)

        self._ref2img_homography = np.array(homography)
        self._img2ref_homography = cv2.invert(self._ref2img_homography)[1]
        print("loaded homography", self._ref2img_homography)
        # update all draw court points
        print("update draw court")
        print("update draw court, before: ", self._draw_court)
        for key in self._court_reference:
            in_point = np.array([*self._court_reference[key]], dtype=np.float32).reshape(-1, 1, 2) 
            self._draw_court[key] = np.int32(cv2.perspectiveTransform(in_point, self._ref2img_homography).reshape(-1, 2))

        print("update draw court, after: ", self._draw_court)
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

    @Slot(int, int, int)
    def handleBallDetected(self, frame_id, x, y):
        # print("handleBallDetected", frame_id, x, y)
        if x == 0 and y == 0: 
            self.ball_xy = None
        else:
            self.ball_xy = (int(self.scale_x * x), int(self.scale_y * y)) # (x, y)
        self.update()

    @Slot(list)
    def handleBounceDetected(self, bounces: list):
        for frame_id, x, y in bounces:
            bounce_xy = (int(self.scale_x * x), int(self.scale_y * y)) 
            # transform to court coordinates
            bounce_xy_arr = np.array(bounce_xy, dtype=np.float32).reshape(-1, 1, 2)
            self.bounce_xy_ref[frame_id] = np.int32(
                cv2.perspectiveTransform(bounce_xy_arr, self._img2ref_homography).reshape(-1, 2))
            self.update()


    def paint(self, painter: QPainter):
        # print("paint event")        
        # draw the court lines
        if self._pixmap is not None:
            painter.drawPixmap(0, 0, self._pixmap)

        self.paint_court(painter)
        self.paint_ball_detection(painter)
        self.paint_mini_map(painter)
        

    def paint_court(self, painter: QPainter):
        # draw the court lines
        # Set the pen for the border
        pen = QPen(QColor(100, 100, 255), 4)  # Blue border with width 4
        painter.setPen(pen)

        # Draw a rectangle that fills the item
        #rect = self.boundingRect()
        #painter.drawRect(rect.adjusted(10, 10, -10, -10))  # Add padding

        #
        for key in self._draw_court:
            painter.drawLine(*self._draw_court[key][0], *self._draw_court[key][1])

        # draw the court reference

        # draw the points for update homography
        for point in self._points_for_update_homography:
            key, point = point.split("-")
            point = int(point)
            painter.setBrush(QColor(255, 0, 0))
            pen = QPen(QColor(255, 0, 255), 2)  # Blue border with width 4
            painter.setPen(pen)
            painter.drawEllipse(self._draw_court[key][point][0] - 5, self._draw_court[key][point][1] - 5, 10, 10)
            
    def paint_ball_detection(self, painter: QPainter):
        if self.ball_xy: 
            # ball_xy = self.ball_xy[self._current_frame_id]
            # print("draw ball_xy {} at {}".format(self.ball_xy, self._current_frame_id))
            pen = QPen(QColor(255, 0, 0), 2)  # Blue border with width 4
            painter.setPen(pen)
            painter.drawEllipse(self.ball_xy[0] - 5, self.ball_xy[1] - 5, 10, 10)

    def paint_mini_map(self, painter: QPainter):

        # TODO: 1. paint court line scaled 
        draw_height = self.height() * 0.6
        ref_height = self._court_reference["left_court_line"][1][1] - self._court_reference["left_court_line"][0][1] 
        draw_scale = draw_height / ref_height

        pen = QPen(QColor(0, 255, 0), 3)  # Blue border with width 4
        painter.setPen(pen)
        draw_ref_cout = {}
        for key in self._court_reference:
            draw_ref_cout[key] = self._court_reference[key] * draw_scale + 10
            painter.drawLine(*draw_ref_cout[key][0], *draw_ref_cout[key][1])



        # TODO: 2. paint bounce point
        for frame_id in self.bounce_xy_ref:
            bounce_draw = self.bounce_xy_ref[frame_id] * draw_scale + 10
            bounce_draw = np.int32(bounce_draw).reshape(-1, 2)
            pen = QPen(QColor(255, 0, 0), 1)  # Blue border with width 4
            painter.setPen(pen)
            painter.setBrush(QColor(255, 0, 0))
            painter.drawEllipse(bounce_draw[0][0] - 3, bounce_draw[0][1] - 3, 6, 6)

