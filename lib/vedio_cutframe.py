import os
import cv2
import numpy as np

from .config import VedioType

IPHONE = "iphone"
CAM = "cam"

# [in]  創建資料夾的路徑
# [out] 創建資料夾的路徑
def create_folder(path):
    # 條件如果資料夾不存在
    if not os.path.isdir(path):
        os.mkdir(path) # 製作資料夾 
    return path

# [in]  video_name 影片路徑
# [in]  vedio_type 用什麼拍的影片 iphone, cam
# [out] 
def cutframe(video_name, vedio_type):
    ### Const value ###############
    HISTORY = 500
    VARTHRESHOLD = 180
    BSHADOWDECTION = True
    ###############################
    
    config = VedioType(IPHONE)      # VedioType(vedio_type)
    ROI_xleft = config.ROI_xleft
    ROI_xright = config.ROI_xright
    ROI_ytop = config.ROI_ytop
    ROI_ydown = config.ROI_ydown
    SIZE_uplmt = config.SIZE_uplmt  # 棒球面積大小上限BALLSIZE_upper_limit
    SIZE_lwlmt = config.SIZE_lwlmt  # 棒球面積大小下限BALLSIZE_lowwer_limit
    DIF_wh = config.DIF_wh          # 棒球區域寬高差需小於 "DIF_wh"
    LMT_wh = config.LMT_wh          # 棒球區域寬高需小於 "LMT_wh"

    ball_frames = []        # 棒球圖片 (48,48)
    video_frame = []        # 影片逐幀圖片
    ball_frame_names = []   # 紀錄是影片的第幾幀
    es = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))   # 做一個kernel
    ''' es=Kernel
    [[0 0 1 0 0]
     [1 1 1 1 1]
     [1 1 1 1 1]
     [1 1 1 1 1]
     [0 0 1 0 0]]'''
    mog = cv2.createBackgroundSubtractorMOG2(HISTORY,VARTHRESHOLD,BSHADOWDECTION)
    cap = cv2.VideoCapture(video_name)  # new一個VideoCapture物件
    
    frame_count = 0
    ret = True
    # 迴圈讀影片的每一個frame
    while ret:
        ret, frame = cap.read() # ret boolean, frame image
        try:
            fgmask = mog.apply(frame)
            th = cv2.threshold(fgmask,244,255,cv2.THRESH_BINARY)[1] # 二值化
            opening = cv2.morphologyEx(th, cv2.MORPH_OPEN, es, iterations=1)    # 開運算
            cont, hierarchy = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)    # 找白點的輪廓
            
            # 迴圈處理所有的
            for c in cont:
                cv2.rectangle(frame,(ROI_xleft,ROI_ytop),(ROI_xright,ROI_ydown),(0,255,0),2)    # 畫ROI區域
                
                # 條件如果白色區域面積符合
                if (cv2.contourArea(c) < SIZE_uplmt and (cv2.contourArea(c) > SIZE_lwlmt)):
                    (x, y, w, h) = cv2.boundingRect(c)  # 取得區塊左上座標xy, 寬高
                    
                    # 條件如果有在ROI區域裡，且大概像小正方形
                    if (abs(w - h) < DIF_wh  and (w < LMT_wh and h < LMT_wh) and (y > ROI_ytop) and (y < ROI_ydown) and (x > ROI_xleft) and (x < ROI_xright)):
                        ROI = frame[(y - 5):(y + h + 5), (x - 5):(x + w + 5)]   # 切有球的區域
                        img = modify_lightness_saturation(
                                ROI)
                        img = cv2.resize(img, (48, 48))                         # 調整照片大小
                        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)        # 畫出切下來的區域
                        ball_frames.append(img)
                        ball_frame_names.append(frame_count)

            video_frame.append(frame)
        except cv2.error as e:
            print("err: ", e)
            continue
        frame_count += 1
    cap.release()
    return np.array(video_frame), np.array(ball_frames), ball_frame_names

def modify_lightness_saturation(img):
    f_Img = img.astype(np.float32)
    f_Img = f_Img / 255.0

    hls_img = cv2.cvtColor(f_Img, cv2.COLOR_BGR2HLS)
    hls_copy = np.copy(hls_img)

    lightness = 130
    saturation = 0

    hls_copy[:, :, 1] = (1 + lightness / 100.0) * hls_copy[:, :, 1]
    hls_copy[:, :, 1][hls_copy[:, :, 1] > 1] = 1

    hls_copy[:, :, 2] = (1 + saturation / 100.0) * hls_copy[:, :, 2]
    hls_copy[:, :, 2][hls_copy[:, :, 2] > 1] = 1

    result_img = cv2.cvtColor(hls_copy, cv2.COLOR_HLS2RGB)
    result_img = ((result_img * 255).astype(np.uint8))
    
    return result_img
