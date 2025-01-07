import cv2
from PySide6.QtCore import QObject, Signal, Slot, QThread
from PySide6.QtGui import QImage
from PickleSwingVision import PickleSwingVision
import TrajectoryPlot

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



class VideoProcessor(QObject):
    gotImage = Signal(int, QImage)
    xPlotReady = Signal(QImage)
    yPlotReady = Signal(QImage)
    currentFrameChanged = Signal(int)
    # playNext = Signal()
    ballDetected = Signal(int, float, float)

    def __init__(self, parent=None):
        super().__init__(parent)
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
        self.thread = QThread()
        self.moveToThread(self.thread)
        print("Load pickle vison Done!!!!1")
        self.currentFrameChanged.emit(-1)
        self.thread.start()


    @Slot(str)
    def read_video(self, path: str):
        self.cap = cv2.VideoCapture(path, cv2.CAP_FFMPEG)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frames = []
        self.get_next_frame()

    def __instancecheck__(self, instance):
        return super().__instancecheck__(instance)

    @Slot()
    def visualize_ball_trajectory(self):
        if self.current_frame < 2:
            return
        process_frames = self.frames[self.current_frame - 2 : self.current_frame + 1]
        ball_track = self.pickle_vision.track_ball(process_frames, self.current_frame)
        self.ballDetected.emit(self.current_frame, ball_track[-1][0], ball_track[-1][1])


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
        while self.keep_playing:
            self.get_next_frame()
        # self.playNext.emit()
        

    @Slot()
    def pause(self):
        self.keep_playing = False

    @Slot()
    def get_next_frame(self):
        ret, frame = self.cap.read()
        if ret:
            self.frames.append(frame)
        else:
            if self.keep_playing:
                self.keep_playing = False
            return None
        self.current_frame += 1
        self.currentFrameChanged.emit(self.current_frame)

        image = cv_to_qimage(self.frames[self.current_frame])
        print(f"Frame {self.current_frame}")
        self.visualize_ball_trajectory()

        self.gotImage.emit(self.current_frame, image)
        # self.prevAvailable.emit(True)
        # if self.keep_playing:
            # self.get_next_frame()
            # self.playNext.emit()

    @Slot()
    def get_prev_frame(self):
        if self.current_frame == 0 or len(self.frames) == 0:
            return None
        self.current_frame -= 1
        self.currentFrameChanged.emit(self.current_frame)
        
        image = cv_to_qimage(self.frames[self.current_frame])
        print(f"Frame {self.current_frame}")

        self.gotImage.emit(self.current_frame, image)

    def get_num_frames(self):
        return len(self.frames)

class Controller(QObject):
    gotImage = Signal(int, QImage)
    xPlotReady = Signal(QImage)
    yPlotReady = Signal(QImage)
    prevAvailable = Signal(bool)
    nextAvailable = Signal(bool)
    playingStatusChanged = Signal(bool)
    ballDetected = Signal(int, float, float)

    # communicate with model
    requestReadVideo = Signal(str)
    requestProcessFrame = Signal()
    requestPlay = Signal()
    requestPause = Signal()
    requestGetNext = Signal()
    requestGetPrev = Signal()

    def __init__(self):
        super().__init__()
        self.videoProcessor = VideoProcessor()
        self.requestReadVideo.connect(self.videoProcessor.read_video)
        self.requestPlay.connect(self.videoProcessor.play)
        self.requestPause.connect(self.videoProcessor.pause)
        self.requestGetNext.connect(self.videoProcessor.get_next_frame)
        self.requestGetPrev.connect(self.videoProcessor.get_prev_frame)

        self.videoProcessor.gotImage.connect(self.handleImageReady)
        self.videoProcessor.xPlotReady.connect(self.handleXplot)
        self.videoProcessor.yPlotReady.connect(self.handleYplot)
        self.videoProcessor.currentFrameChanged.connect(self.handleCurrentFrameChanged)
        self.videoProcessor.ballDetected.connect(self.handleBallDetected)
        
    @Slot(str)
    def read_video(self, path: str):
        self.requestReadVideo.emit(path)

    @Slot()
    def play(self):
        self.requestPlay.emit()
        self.playingStatusChanged.emit(True)
        
    @Slot()
    def pause(self):
        self.requestPause.emit()
        self.playingStatusChanged.emit(False)

    @Slot()
    def get_next_frame(self):
        self.requestGetNext.emit()

    @Slot()
    def get_prev_frame(self):
        self.requestGetPrev.emit()

    # process data from video processor
    @Slot(QImage)
    def handleXplot(self, image):
        self.xPlotReady.emit(image)

    @Slot(QImage)
    def handleYplot(self, image):
        self.yPlotReady.emit(image)

    @Slot(int, QImage)
    def handleImageReady(self, frame_id, image):
        self.gotImage.emit(frame_id, image)

    @Slot(int)
    def handleCurrentFrameChanged(self, currentFrame):
        if currentFrame <= 0:
            self.prevAvailable.emit(False)
        else:
            self.prevAvailable.emit(True)
        if currentFrame == self.videoProcessor.get_num_frames() - 1:
            self.nextAvailable.emit(False)
        else:
            self.nextAvailable.emit(True)

    @Slot(int, float, float)
    def handleBallDetected(self, frame_id, x, y):
        self.ballDetected.emit(frame_id, x, y)
