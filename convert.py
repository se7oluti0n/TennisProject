from ball_detector import BallDetector
import argparse
import torch

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model", type=str, help="path to pretrained model for ball detection"
    )
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"

    print(torch.__version__)
    print(torch.onnx.__name__)
    ball_detector = BallDetector(args.model, device)
    ball_detector.convert_to_onnx() 
