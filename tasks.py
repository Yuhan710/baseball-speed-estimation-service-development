from celery import Celery
from cutBall import cutball
from pred_RPM_pred_ip import pred
import json

app = Celery(
    'tasks',
    backend='redis://127.0.0.1:6379/1',
    broker='redis://127.0.0.1:6379/1',
)

# 定義工作函數


@app.task
def pred_spinrate(id, video_id, video_path, fps):
    # print("123\n\n")

    ball_to_line_img = cutball(video_path, fps)
    pred_spinrate = pred(ball_to_line_img, fps)
    data = json.loads(pred_spinrate)
    spinrate = data["pred"]
    return (id, video_id, spinrate)
