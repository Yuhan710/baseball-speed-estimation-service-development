
CREATE TABLE user (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  profile_pic TEXT NOT NULL
);


CREATE TABLE video (
  video_id TEXT NOT NULL,
  id TEXT NOT NULL ,
  origin_filename TEXT NOT NULL,
  upload_video TEXT NOT NULL,
  upload_time TEXT NOT NULL,
  final_video TEXT,
  ball_spinrate TEXT
);
