from cutBall import cutball
from function import *
from pred_RPM_pred_ip import pred

def pred_spinrate(video_path):
    ball_to_line_img = cutball(video_path)
    df = get_dataframe(ball_to_line_img)
    pred_spinrate = pred(df)
    print(pred_spinrate)

pred_spinrate("./file/upload_video/cam_7_88.avi")