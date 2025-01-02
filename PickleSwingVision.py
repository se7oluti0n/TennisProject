from bounce_detector import BounceDetector
# from person_detector import PersonDetector
from ball_detector import BallDetector


class PickleSwingVision:
    def __init__(self, args, device):
        self.ball_track = None
        self.bounces = None
        self.match_points = None
        print('ball detection')

        self.ball_detector = BallDetector(args[ "path_ball_track_model" ], device)
        self.bounce_detector = BounceDetector(args[ "path_bounce_model" ])
        self._ball_trajectory = {} 

    def get_ball_trajectory(self):
        return self._ball_trajectory

    #brief: function to track the ball
    #params: frames: list of 3 consecutive video frames 
    def track_ball(self, frames, frame_index):
        ball_track = self.ball_detector.infer_model(frames)
        self._ball_trajectory[frame_index] = ball_track
        return ball_track

    #brief: function to detect bounces
    #params: ball_track: list of (x,y) ball coordinates from 
    # the end of last swing
    #returns: bounces: list of image numbers where ball touches the ground
    # and where the ball touch the racquet
    def bounce_detect(self, ball_track):
        x_ball = [x[0] for x in ball_track]
        y_ball = [x[1] for x in ball_track]
        bounces = self.bounce_detector.predict(x_ball, y_ball)
        return bounces


    def smooth_ball_track(self, ball_track):
        x_ball = [x[0] for x in ball_track]
        y_ball = [x[1] for x in ball_track]
        x_ball, y_ball = self.bounce_detector.smooth_predictions(x_ball, y_ball)
        return x_ball, y_ball


