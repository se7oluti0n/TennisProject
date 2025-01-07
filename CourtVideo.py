from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QImage
from VideoProcessor import VideoProcessor

class VideoController(QObject):
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
        self.requestPlay.connect(self.videoProcessor.startPlayLoop)
        self.requestPause.connect(self.videoProcessor.pausePlayLoop)
        self.requestGetNext.connect(self.videoProcessor.processNextFrame)
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
