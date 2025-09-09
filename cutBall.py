
from function import *
import time



def cutball(video_path, fps):
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"
    print("cut function start...")

    # video_frames,ball_frames,ball_frame_names= cutframe_iphone(video_name)
    ball_cuts = ball_cutframe(video_path, fps)
    video_frames = ball_cuts.frame_return()
    ball_frames = ball_cuts.extract_ball_return()
    
    return ball_frames
