from court_detector import CourtDetector
import argparse
import cv2

def read_video(path_video):
    cap = cv2.VideoCapture(path_video)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frames = []
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            frames.append(frame)
        else:
            break    
    cap.release()
    return frames, fps

if __name__ == '__main__':
    # Create a CourtDetector object
    court_detector = CourtDetector()
    parser = argparse.ArgumentParser()
    parser.add_argument('--path_input_video', type=str, help='path to input video')
    args = parser.parse_args()
    
    frames, fps = read_video(args.path_input_video) 


    print('court detection')
    homography_marices = []

    court_detector = CourtDetector()

    print("Detecting the court and the players...")
    for frame_i in range(len(frames)):
        frame = frames[frame_i]

        if frame_i == 0:
            lines = court_detector.detect(frame, verbose=1)
            break

