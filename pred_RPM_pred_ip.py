import matplotlib.pyplot as plt
import random
import tensorflow as tf
import pandas as pd
import cv2
import numpy as np
from tensorflow.keras import backend as K
from tensorflow.keras.models import load_model
import json


def root_mean_squared_error(y_true, y_pred):
    msle = tf.keras.losses.MeanSquaredLogarithmicError()
    return K.sqrt(msle(y_true, y_pred))


model = load_model('./Spin_model/spinrate_mask_blue_to_write.ckpt',
                   custom_objects={'root_mean_squared_error': root_mean_squared_error})
# model2 = load_model('./Spin_model/spinrate__240FPS.ckpt',
#                    custom_objects={'root_mean_squared_error': root_mean_squared_error})

model2 = load_model('./Spin_model/End2End_MatchLineball_Test_20220917_epoch_20.h5')


def pred(ball_to_line, fps):
    # print("pred start...")
    # preds = []

    # for i in range(0, len(ball_to_line)-5):

    #     for j in range(5):

    #         if (j == 0):
    #             img = ball_to_line[i + j]
    #             img = cv2.resize(img, (48, 48))
    #             temp = img
    #         else:
    #             img1 = ball_to_line[i + j]
    #             img1 = cv2.resize(img1, (48, 48))
    #             temp = np.concatenate((temp, img1), -1)
    #     temp = temp / 255.0

    #     temp = np.expand_dims(temp, axis=0)
    #     pred = model2.predict(temp, verbose=0)
    #     # print(pred[0][0])
    #     preds.append(pred[0][0])
    # preds = int(np.median(np.array(preds)))
    # json_pred = json.dumps({"pred": preds})
    # return json_pred

    print("pred start...")
    preds = []

    # img_temp = int(fps / 240)  
    # new_ball_to_line = ball_to_line[::img_temp]

    ReCollect_Ball2Line = []
    VideoFrameCount_Buf = []
    for k, v in ball_to_line.items():
        if len(VideoFrameCount_Buf) == 0:
            VideoFrameCount_Buf.append(k)
        else:
            if k - VideoFrameCount_Buf[-1] == int(fps / 240):
                VideoFrameCount_Buf.append(k)
                if len(VideoFrameCount_Buf) == 5:
                    temp = ball_to_line[VideoFrameCount_Buf[0]]
                    for j in range(1, 5):
                        img = ball_to_line[VideoFrameCount_Buf[j]]
                        temp = np.concatenate((temp, img), -1)
                    ReCollect_Ball2Line.append(temp)
                    VideoFrameCount_Buf = VideoFrameCount_Buf[1:]
            else:
                VideoFrameCount_Buf = [k]

    for imgs in ReCollect_Ball2Line:
        
        imgs = imgs / 255.0
        imgs = np.expand_dims(imgs, axis=0)
        pred = model2.predict(imgs, verbose=0)
        preds.append(pred[0][0] * 3000 + 600)

    preds = int(np.median(np.array(preds)))
    json_pred = json.dumps({"pred": preds})
    return json_pred

    # new_ball_to_line = ball_to_line
    # for i in range(0, len(new_ball_to_line) - 5):
    #     temp = new_ball_to_line[i]
    #     for j in range(1, 5):
    #         img = new_ball_to_line[i + j]
    #         temp = np.concatenate((temp, img), -1)

    #     temp = temp / 255.0
    #     temp = np.expand_dims(temp, axis=0)
    #     pred = model2.predict(temp, verbose=0)
    #     preds.append(pred[0][0])

    # preds = int(np.median(np.array(preds)))
    # json_pred = json.dumps({"pred": preds})
    # return json_pred







    # print("pred start...")
    # preds = []

    # img_count = 1
   
    # for i in range(0, len(ball_to_line) - 5, img_count):
    #     if (abs((i + 1) /fps - img_count /240) ) <  (abs((i + 2) /fps - img_count /240) )
    #         temp = ball_to_line[i]
    #         img_count = img_count + 1
    
    #     else:
    #         continue
    #     for j in range(1, 5):
    #         img = ball_to_line[i + j]
    #         temp = np.concatenate((temp, img), -1)

    #     temp = temp / 255.0
    #     temp = np.expand_dims(temp, axis=0)
    #     pred = model2.predict(temp, verbose=0)
    #     preds.append(pred[0][0])

    # preds = int(np.median(np.array(preds)))
    # json_pred = json.dumps({"pred": preds})
    # return json_pred






   
