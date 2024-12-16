#!/usr/bin/bash
python3 main.py --path_ball_track_model models/model_tracknet.pt --path_court_model models/model_tennis_court_det.pt --path_bounce_model models/ctb_regr_bounce.cbm --path_input_video input_videos/input_video.mp4 --path_output_video output_videos/output_video.mp4
