from PySide6.QtCore import QObject, Signal, Slot, QPoint
from VideoProcessor import VideoProcessor

class ChartController(QObject):
    xBallTrajectoryUpdated = Signal(float, float)
    yBallTrajectoryUpdated = Signal(float, float)
    xBounceUpdated = Signal(float, float)
    yBounceUpdated = Signal(float, float)
    axisXUpdated = Signal(float)
    axisYUpdated = Signal(float)

    def __init__(self, VideoProcessor: VideoProcessor):
        super().__init__()
        self.videoProcessor = VideoProcessor
        self.videoProcessor.ballDetected.connect(self.handleBallTrajectoryUpdated)
        self.videoProcessor.bouncesDetected.connect(self.handleBounceDetected)
        self.maxX = 100
        self.maxY = 100

    @Slot(int, float, float)
    def handleBallTrajectoryUpdated(self, frame_id, x, y):
        # point_x = QPoint(frame_id, x)
        # point_y = QPoint(frame_id, y)
        if x > self.maxY:
            self.maxY = x + 10
            self.axisYUpdated.emit(self.maxY)
        if y > self.maxY:
            self.maxY = y + 10
            self.axisYUpdated.emit(self.maxY)
        if frame_id > self.maxX:
            self.maxX = self.maxX + 50
            self.axisXUpdated.emit(self.maxX)

        self.xBallTrajectoryUpdated.emit(frame_id, x)
        self.yBallTrajectoryUpdated.emit(frame_id, y)

    @Slot(list)
    def handleBounceDetected(self, bounces):

        if len(bounces) > 0:
            frame_id, x, y = bounces[-1]
            # point_x = QPoint(frame_id, x)
            # point_y = QPoint(frame_id, y)
            self.xBounceUpdated.emit(frame_id, x)
            self.yBounceUpdated.emit(frame_id, y)
