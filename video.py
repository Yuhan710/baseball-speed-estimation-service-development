from flask_login import UserMixin

from db import get_db

# import sqlite3


class Video(UserMixin):
    def __init__(self, video_id, id_, origin_filename, upload_video, upload_time, final_video, ball_spinrate):
        self.video_id = video_id
        self.id = id_
        self.origin_filename = origin_filename
        self.upload_video = upload_video
        self.upload_time = upload_time
        self.final_video = final_video
        self.ball_spinrate = ball_spinrate

    @staticmethod
    def get(user_id):
        db = get_db()
        video = db.execute(
            "SELECT * FROM video WHERE id = ?", (user_id,)
        ).fetchone()
        if not video:
            return None

        video = Video(
            video_id=video[0],
            id_=video[1],
            origin_filename=video[2],
            upload_video=video[3],
            upload_time=video[4],
            final_video=video[5],
            ball_spinrate=video[6]

        )
        return video

    @staticmethod
    def create(video_id, id_, origin_filename, upload_video, upload_time, final_video, ball_spinrate):
        db = get_db()
        db.execute(
            "INSERT INTO video (video_id, id, origin_filename, upload_video, upload_time, final_video, ball_spinrate) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (video_id, id_, origin_filename, upload_video,
             upload_time, final_video, ball_spinrate),
        )
        db.commit()

    @staticmethod
    def update(id_, video_id, ball_spinrate):
        db = get_db()
        db.execute(
            "UPDATE video set ball_spinrate = ? where video_id = ? and id = ?",
            (ball_spinrate, video_id, id_),
        )
        db.commit()

    def get_video_info(userid):
        db = get_db()

        sql_search = "SELECT * from video where video.id = ? Order by upload_time DESC;"
        params_search = (userid,)
        cursor = db.execute(sql_search, params_search)
        video_info = []
        rows = cursor.fetchall()
        for row in rows:
            line = []
            for i in row[2:]:
                line.append(i)
            video_info.append(line)
        return video_info








    def get_uservideo_info():
            db = get_db()
    
            user = db.execute(
                "SELECT * FROM user WHERE email = ?", ("chihyucho47@gmail.com",)
            ).fetchone()
            sql_search = "SELECT * from video where video.id = ? Order by upload_time DESC;"
            params_search = (user[0],)
            cursor = db.execute(sql_search, params_search)
            video_info = []
            rows = cursor.fetchall()
            for row in rows:
                line = []
                for i in row[2:]:
                    line.append(i)
                video_info.append(line)
            print(video_info)
            print("\n")
# def add_upload_video(origin_filename, upload_video, upload_time, userid):
#     conn = sqlite3.connect("database.db")
#
#     with conn.cursor() as cursor:
#         sql_add='INSERT INTO video(origin_filename, upload_video, upload_time, userid) VALUES（?, ?, ?, ?）'
#         params_add = (origin_filename,upload_video,upload_time,userid)
#         cursor.execute(sql_add, params_add)
#         conn.commit()

# def add_final_video(final_video, ball_spinrate, upload_video):
#     conn = sqlite3.connect("database.db")
#
#     with conn.cursor() as cursor:
#         sql_add='UPDATE video SET final_video = ?, ball_spinrate = ? WHERE upload_video = ?'
#         params_add = (final_video, ball_spinrate, userid)
#         cursor.execute(sql_add, params_add)
#         conn.commit()
