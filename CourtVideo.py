import cv2
from PySide6.QtCore import QObject, Signal, Slot, Property
from PySide6.QtGui import QImage
from PySide6.QtQml import QmlElement
from PickleSwingVision import PickleSwingVision

def cv_to_qimage(cv_img):
    """Convert OpenCV image to QImage."""
    height, width, channel = cv_img.shape
    bytes_per_line = channel * width
    # Convert BGR to RGB
    cv_img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    qimg = QImage(cv_img_rgb.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
    return qimg

QML_IMPORT_NAME = "CourtVideo"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0  # Optional

@QmlElement
class CourtVideo(QObject):

    gotImage = Signal(int, QImage)
    prevAvailable = Signal(bool)
    nextAvailable = Signal(bool)
    ballDetected = Signal(int, int, int)

    def __init__(self):
        super().__init__()
        self.current_frame = -1
        self.frames = []
        self.pickle_vision = PickleSwingVision({"path_ball_track_model": "models/model_tracknet.pt", "path_bounce_model": "models/ctb_regr_bounce.cbm"}, "cuda")
        print("Load pickle vison Done!!!!1")

    @Property(bool, notify=prevAvailable)
    def checkPrev(self):
        return self.current_frame > 0

    @Property(int, notify=nextAvailable)
    def checkNext(self):
        return self.current_frame < len(self.frames) - 1

    @Slot(str)
    def read_video(self, path: str):
        self.cap = cv2.VideoCapture(path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frames = []
        self.get_next_frame()

    @Slot()
    def process_current_frame(self):
        if self.current_frame < 2:
            return
        process_frames = self.frames[self.current_frame - 2 : self.current_frame + 1]
        ball_track = self.pickle_vision.track_ball(process_frames, self.current_frame)
        # emit to visualize on CourtView
        if len(ball_track) > 0 and ball_track[-1][0] is not None and ball_track[-1][1] is not None:
            print("Ball track: ", ball_track)
            self.ballDetected.emit(self.current_frame, ball_track[-1][0], ball_track[-1][1])
    
    @Slot()
    def get_next_frame(self):
        ret, frame = self.cap.read()
        if ret:
            self.frames.append(frame)
        if len(self.frames) > 0:
            self.nextAvailable.emit(True)
        if self.current_frame == len(self.frames) - 1:
            return None
        self.current_frame += 1
        self.prevAvailable.emit(True)
        image =  cv_to_qimage(self.frames[self.current_frame])
        print(f"Frame {self.current_frame}")
        self.gotImage.emit(self.current_frame, image)
        self.process_current_frame()

    @Slot()
    def get_prev_frame(self):
        if self.current_frame == 0 or len(self.frames) == 0:
            return None
        self.current_frame -= 1
        image = cv_to_qimage(self.frames[self.current_frame])
        print(f"Frame {self.current_frame}")

        self.gotImage.emit(self.current_frame, image)

