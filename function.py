import cv2
import os
import numpy as np
from tensorflow.keras import backend as K
import tensorflow as tf
import pandas as pd
import argparse
import time
from pathlib import Path
import onnxruntime as ort
# import warningsc
# import torch
# import torch.backends.cudnn as cudnn
# from numpy import random

# from models.experimental import attempt_load
# from utils.datasets import LoadStreams, LoadImages
# from utils.general import check_img_size, check_requirements, check_imshow, non_max_suppression, apply_classifier, \
#     scale_coords, xyxy2xywh, strip_optimizer, set_logging, increment_path
# from utils.plots import plot_one_box
# from utils.torch_utils import select_device, load_classifier, time_synchronized, TracedModel


def create_folder(path):
    # imgPath = './ball/' + date + '_' + foldName
    if not os.path.isdir(path):
        os.mkdir(path)
    else:
        pass
    return path


class VideoReader:
    def __init__(self, video_path):
        self.video_path = video_path
        self.video_capture = None

    def open(self):
        self.video_capture = cv2.VideoCapture(self.video_path)
        video_width = self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        video_height = self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)

        if not self.video_capture.isOpened():
            raise ValueError("無法打開影片檔案")
        
        return video_width, video_height

    def read_frame(self):
        ret, frame = self.video_capture.read()

        if ret:
            return frame
        else:
            return None

    def close(self):
        if self.video_capture:
            self.video_capture.release()
            self.video_capture = None


class ball_cutframe:

    def __init__(self, video_name, fps):
        self.video_name = video_name
        self.model_path = './yolov7.onnx'
        self.session = ort.InferenceSession(self.model_path, providers=[
                                            'DmlExecutionProvider', 'CPUExecutionProvider'])
        self.input_size = (384, 288)
        self.ball = {}
        self.frame = []
        self.video_reader = None
        self.fps = fps
        self.ball_extract_frame()

    def ball_extract_frame(self):
        self.video_reader = VideoReader(self.video_name)
        w, h = self.video_reader.open()
        skip_frame_num = int(self.fps / 240)  
        count = 0
        while True:
                frame = self.video_reader.read_frame()

                if frame is None:
                    break
                else:
                    if count % skip_frame_num == 0:
                        inp = cv2.dnn.blobFromImage(frame, 1/255.0, self.input_size)

                        outputs = self.session.run(None, {"images": inp})

                        for batch_id, x0, y0, x1, y1, class_id, score in outputs[0]:
                            if class_id == 32.0:
                                x0 = int(round(x0 * w / self.input_size[0]))#Fix 720->frame size
                                x1 = int(round(x1 * w / self.input_size[0]))#Fix 720->frame size
                                y0 = int(round(y0 * h / self.input_size[1]))#Fix 540->frame size
                                y1 = int(round(y1 * h / self.input_size[1]))#Fix 540->frame size
                                self.ball[count] = cv2.resize(frame[y0:y1, x0:x1], (48, 48))
                                self.frame.append(frame)
                    count += 1

    def extract_ball_return(self):
        return self.ball
        # return np.array(self.ball)

    def frame_return(self):
        return np.array(self.frame)

    def close(self):
        if self.video_reader:
            self.video_reader.close()


def root_mean_squared_error(y_true, y_pred):
    msle = tf.keras.losses.MeanSquaredLogarithmicError()
    return K.sqrt(msle(y_true, y_pred))
