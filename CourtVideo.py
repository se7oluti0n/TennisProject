import cv2
from PySide6.QtCore import QObject, Signal, Slot, Property
from PySide6.QtGui import QImage
from PySide6.QtQml import QmlElement
from PickleSwingVision import PickleSwingVision
import TrajectoryPlot
import time


def cv_to_qimage(cv_img):
    """Convert OpenCV image to QImage."""
    height, width, channel = cv_img.shape
    bytes_per_line = channel * width
    # Convert BGR to RGB
    cv_img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    qimg = QImage(
        cv_img_rgb.data, width, height, bytes_per_line, QImage.Format.Format_RGB888
    )
    return qimg


QML_IMPORT_NAME = "CourtVideo"
QML_IMPORT_MAJOR_VERSION = 1
QML_IMPORT_MINOR_VERSION = 0  # Optional


@QmlElement
class CourtVideo(QObject):

    gotImage = Signal(int, QImage)
    xPlotReady = Signal(QImage)
    yPlotReady = Signal(QImage)
    prevAvailable = Signal(bool)
    nextAvailable = Signal(bool)
    isPlaying = Signal(bool)
    ballDetected = Signal(int, int, int)
    playNext = Signal()

    def __init__(self):
        super().__init__()
        self.current_frame = -1
        self.frames = []
        self.pickle_vision = PickleSwingVision(
            {
                "path_ball_track_model": "models/model_tracknet.pt",
                "path_bounce_model": "models/ctb_regr_bounce.cbm",
            },
            "cuda",
        )
        self.ball_trajectory = []
        self.keep_playing = False
        # self.connect(self.playNext, self.get_next_frame)
        print("Load pickle vison Done!!!!1")

    @Property(bool, notify=prevAvailable)
    def checkPrev(self):
        return self.current_frame > 0

    @Property(bool)
    def isPlaying(self):
        return self.keep_playing

    @Property(int, notify=nextAvailable)
    def checkNext(self):
        return self.current_frame < len(self.frames) - 1

    @Slot(str)
    def read_video(self, path: str):
        self.cap = cv2.VideoCapture(path, cv2.CAP_FFMPEG)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frames = []
        self.get_next_frame()


    @Slot()
    def visualize_bounce_detection(self):
       bounces =  self.pickle_vision.bounce_detect(self.ball_trajectory)


    @Slot()
    def visualize_ball_trajectory(self):
        if self.current_frame < 2:
            return
        process_frames = self.frames[self.current_frame - 2 : self.current_frame + 1]
        ball_track = self.pickle_vision.track_ball(process_frames, self.current_frame)


        if not self.ball_trajectory:
            self.ball_trajectory = ball_track
        else:
            self.ball_trajectory.append(ball_track[-1])
        

        # unzip ball_track to x track and y track

        x_track, y_track = self.pickle_vision.smooth_ball_track(self.ball_trajectory)
        x_track = [x if x is not None else 0 for x in x_track]
        y_track = [y if y is not None else 0 for y in y_track]

        # print("x_track: ", x_track)
        # print("y_track: ", y_track)
        bounces =  self.pickle_vision.bounce_detect(self.ball_trajectory)
        print("bounces: ", bounces)

        # plot ball track
        x_plot = TrajectoryPlot.matplotlib_figure_to_qimage(x_track, bounces=bounces)
        y_plot = TrajectoryPlot.matplotlib_figure_to_qimage(y_track, bounces=bounces)

        print(f"x_plot: {x_plot.width()} {x_plot.height()}")
        print(f"y_plot: {y_plot.width()} {y_plot.height()}")

        self.xPlotReady.emit(x_plot)
        self.yPlotReady.emit(y_plot)

        # emit to visualize on CourtView
        if (
            len(ball_track) > 0
            and ball_track[-1][0] is not None
            and ball_track[-1][1] is not None
        ):
            print("Ball track: ", ball_track)
            self.ballDetected.emit(
                self.current_frame, ball_track[-1][0], ball_track[-1][1]
            )

    @Slot()
    def play(self):
        self.keep_playing = True
        # self.get_next_frame()
        self.playNext.emit()

    @Slot()
    def pause(self):
        self.keep_playing = False

    @Slot()
    def get_next_frame(self):
        ret, frame = self.cap.read()
        if ret:
            self.frames.append(frame)
        if len(self.frames) > 0:
            self.nextAvailable.emit(True)
        if self.current_frame == len(self.frames) - 1:
            if self.keep_playing:
                self.keep_playing = False
            return None
        self.current_frame += 1
        image = cv_to_qimage(self.frames[self.current_frame])
        print(f"Frame {self.current_frame}")
        self.visualize_ball_trajectory()

        self.gotImage.emit(self.current_frame, image)
        self.prevAvailable.emit(True)
        if self.keep_playing:
            # self.get_next_frame()
            self.playNext.emit()

    @Slot()
    def get_prev_frame(self):
        if self.current_frame == 0 or len(self.frames) == 0:
            return None
        self.current_frame -= 1
        image = cv_to_qimage(self.frames[self.current_frame])
        print(f"Frame {self.current_frame}")

        self.gotImage.emit(self.current_frame, image)
