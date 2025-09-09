from flask_login import UserMixin

from db import get_db

# import sqlite3
class User(UserMixin):
    def __init__(self, id_, name, email, profile_pic):
        self.id = id_
        self.name = name
        self.email = email
        self.profile_pic = profile_pic

    @staticmethod
    def get(user_id):
        db = get_db()
        user = db.execute(
            "SELECT * FROM user WHERE id = ?", (user_id,)
        ).fetchone()
        if not user:
            return None

        user = User(
            id_=user[0], name=user[1], email=user[2], profile_pic=user[3]
        )
        return user

    @staticmethod
    def create(id_, name, email, profile_pic):
        db = get_db()
        db.execute(
            "INSERT INTO user (id, name, email, profile_pic) "
            "VALUES (?, ?, ?, ?)",
            (id_, name, email, profile_pic),
        )
        db.commit()

   
# def get_video_info(userid):
#     conn = sqlite3.connect("database.db")
# 
#     with conn.cursor() as cursor:
#         sql_search = "SELECT * from video where video.userid = ? Oder by upload_time DESC;"
#         params_search = (userid)
#         cursor.execute(sql_search,params_search)
#         video_info = []
#         for row in cursor:
#             line = []
#             for i in row[:-1]:
#                 line.append(i)
#             video_info.append(line)
#     return video_info

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
