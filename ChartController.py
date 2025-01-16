from PySide6.QtCore import QObject, Signal, Slot, QPoint
from VideoProcessor import VideoProcessor

class ChartController(QObject):
    xBallTrajectoryUpdated = Signal(float, float)
    yBallTrajectoryUpdated = Signal(float, float)
    bounceUpdated = Signal(float, float)
    axisXUpdated = Signal(float, float)
    axisYUpdated = Signal(float)
    ballTrajectoryLoaded = Signal(list)
    bouncesLoaded = Signal(list)
    currentFrameChanged = Signal(int)

    def __init__(self, VideoProcessor: VideoProcessor):
        super().__init__()
        self.videoProcessor = VideoProcessor
        self.videoProcessor.ballDetected.connect(self.handleBallTrajectoryUpdated)
        self.videoProcessor.bouncesDetected.connect(self.handleBounceDetected)
        self.videoProcessor.ballTrajectoryLoaded.connect(self.handleBallTrajectoryLoaded)
        self.videoProcessor.bouncesLoaded.connect(self.handleBouncesLoaded)
        self.videoProcessor.currentFrameChanged.connect(self.handleCurrentFrameChanged)
        self.maxX = 100
        self.maxY = 100
        self.lastBounce = -1
        self.moveMode = False
        self.lastMousePos =  -1
        self.xScale = 100

    @Slot(int)
    def handleCurrentFrameChanged(self, frame_id):
        self.currentFrameChanged.emit(frame_id)

    @Slot(int)
    def handleReplayAtFrame(self, frame_id: int):
        self.videoProcessor.replay_frame(frame_id)

    @Slot(float)
    def handleLeftMousePressed(self, x):
        self.moveMode = True
        self.lastMousePos = x

    @Slot()
    def handleLeftMouseReleased(self):
        self.moveMode = False

    @Slot(float)
    def handleMouseMove(self, x):
        if self.moveMode:
            self.axisXUpdated.emit(self.maxX + (self.lastMousePos - x) * 0.5, self.xScale)

    @Slot()
    def handleRightMouseClicked(self):
        print("Right mouse clicked, handle replay point")

    @Slot(int, float, float)
    def handleBallTrajectoryUpdated(self, frame_id, x, y):
        if x > self.maxY:
            self.maxY = x + 10
            self.axisYUpdated.emit(self.maxY)
        if y > self.maxY:
            self.maxY = y + 10
            self.axisYUpdated.emit(self.maxY)
        if frame_id > self.maxX:
            self.maxX = self.maxX + 50
            self.axisXUpdated.emit(self.maxX, self.xScale)

        self.xBallTrajectoryUpdated.emit(frame_id, x)
        self.yBallTrajectoryUpdated.emit(frame_id, y)

    @Slot(list)
    def handleBounceDetected(self, bounces):

        if len(bounces) > 0:
            frame_id, _, _ = bounces[-1]
            if frame_id != self.lastBounce:
                print("Bounce detected: ", frame_id)
                self.bounceUpdated.emit(frame_id, 0)
                self.lastBounce = frame_id

    @Slot(list)
    def handleBallTrajectoryLoaded(self, trajectory):
        self.ballTrajectoryLoaded.emit(trajectory)


    @Slot(list)
    def handleBouncesLoaded(self, bounces):
        self.bouncesLoaded.emit(bounces)
