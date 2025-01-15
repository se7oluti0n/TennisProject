from PickleSwingVision import PickleSwingVision
import TrajectoryPlot
from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtGui import QImage
import cv2
import numpy as np
import os
import json


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
    ballDetected = Signal(int, float, float)
    bouncesDetected = Signal(list)

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
        self.track_ball = True
        self.thread = QThread()
        self.moveToThread(self.thread)
        self.currentFrameChanged.emit(-1)
        self.thread.start()
        self.video_path = None

    def save(self, path):

        trajectory_path = path + "_ball_trajectory.npy"
        bounces_path = path + "_bounces.npy"

        ball_trajectory_array = np.asarray(self.ball_trajectory)
        np.save(trajectory_path , ball_trajectory_array)

        bounces_array = np.asarray(self.bounces)
        np.save(bounces_path, bounces_array)


        project_object = {
            "video_file": self.video_path,
            "ball_trajectory": trajectory_path, 
            "bounces": bounces_path
        }

        with open(path + ".json", "w") as outfile:
            json.dump(project_object, outfile)

    def load(self, path):
        with open(path + ".json", "r") as f:
            project_object = json.load(f)

        self.read_video(project_object["video_file"])
        self.ball_trajectory = np.load(project_object["ball_trajectory"], allow_pickle=True)
        self.bounces = np.load(project_object["bounces"], allow_pickle=True)


    @Slot()
    def stop(self):
        try:
            self.cap.release()

            self.keep_playing = False
            self.thread.quit()
            self.thread.wait()
        except:
            print("Exception when trying to stop thread")

    @Slot(str)
    def read_video(self, path: str):
        self.cap = cv2.VideoCapture(path, cv2.CAP_FFMPEG)
        self.video_path = path
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frames = []

    @Slot()
    def trackBallTrajectory(self):
        if self.current_frame < 2:
            return
        process_frames = self.frames[self.current_frame - 2 : self.current_frame + 1]
        # ball_track = self.pickle_vision.track_ball(process_frames, self.current_frame)
        ball_track = []
        ball2 = self.pickle_vision.track_ball2(self.frames[self.current_frame])
        if ball2:
            result = ball2[1]
            ball_track.append(((result[0] + result[2]) / 2, (result[1] + result[3]) / 2))
        else:
            ball_track.append((None, None))
        
        if not self.ball_trajectory:
            self.ball_trajectory = ball_track
        else:
            self.ball_trajectory.append(ball_track[-1])

        x_track, y_track = self.pickle_vision.smooth_ball_track(self.ball_trajectory)

        x_track = [x if x is not None else 0 for x in x_track]
        y_track = [y if y is not None else 0 for y in y_track]

        self.bounces = self.pickle_vision.bounce_detect(self.ball_trajectory)
        self.bouncesDetected.emit([(frame_id, x_track[frame_id], y_track[frame_id]) for frame_id in self.bounces])

        # plot ball track

        # emit to visualize on CourtView
        if (
            len(ball_track) > 0
            and ball_track[-1][0] is not None
            and ball_track[-1][1] is not None
        ):
            # print("Ball track: ", ball_track)
            self.ballDetected.emit(
                self.current_frame, ball_track[-1][0], ball_track[-1][1]
            )


    @Slot(int)
    def replay_frame(self, frame_id: int):
        self.current_frame = frame_id - 1
        self.track_ball = False
        self.keep_playing = False
        self.processNextFrame()

    @Slot()
    def startPlayLoop(self):
        self.keep_playing = True
        while self.keep_playing:
            self.processNextFrame()

    def pausePlayLoop(self):
        print("---------------------------- pause play loop")
        self.keep_playing = False

    @Slot()
    def processNextFrame(self):
        ret, frame = self.cap.read()
        if ret:
            self.frames.append(frame)
        else:
            if self.keep_playing:
                self.keep_playing = False
            if self.current_frame == len(self.frames) - 1:
                return None
        self.current_frame += 1
        self.currentFrameChanged.emit(self.current_frame)

        image = cv_to_qimage(self.frames[self.current_frame])
        self.gotImage.emit(self.current_frame, image)

        if self.track_ball:
            self.trackBallTrajectory()

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
