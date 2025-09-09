# Python standard libraries
import json
import os
import sqlite3
import sys

# Third-party libraries
from flask import Flask, render_template, redirect, request, url_for, jsonify, send_from_directory, flash
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
import requests
from werkzeug.utils import secure_filename
# Internal imports
from db import init_db_command
from user import User
from video import Video
from cutBall import cutball
from function import *
from celery import Celery
from datetime import datetime
from pred_RPM_pred_ip import pred

# from tasks import add
from tasks import pred_spinrate

# Configuration
GOOGLE_CLIENT_ID = ""
GOOGLE_CLIENT_SECRET = ""
GOOGLE_DISCOVERY_URL = ""

domain_name = 'https://baseball.homelab.tw'


upload_count = 0
dir = './file/upload_video/'
for path in os.listdir(dir):
    if os.path.isfile(os.path.join(dir, path)):
        upload_count += 1
# print(upload_count)

# Flask app setup
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
app.config['UPLOAD_FOLDER'] = './file/upload_video/'

celery = Celery(
    'tasks',
    broker='redis://127.0.0.1:6379/1',
    backend='redis://127.0.0.1:6379/1',
)
tasks = []
# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)

# Naive database setup
try:
    init_db_command()
except sqlite3.OperationalError:
    # Assume it's already been created
    pass

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Flask-Login helper to retrieve a user from our db


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


def load_video(user_id):
    return Video.get(user_id)
# Homepage


@app.route("/")
def index():
    if current_user.is_authenticated:
        userid = current_user.id
        # video = load_video(userid)
        if tasks:
            for task in tasks:
                result = pred_spinrate.AsyncResult(task)
                if result.ready():
                    if result.state == 'SUCCESS':
                        result = result.get()
                        id, video_id, ball_spinrate = result
                        Video.update(id, video_id, ball_spinrate)
                        print("update success!")
                        tasks.remove(task)
                    elif result.state == 'FAILURE':
                        print("Failure!")
                else:
                    pass

        video = Video.get_video_info(userid)
        # uservideo = Video.get_uservideo_info() #0828

        return render_template(
            "index.html",
            user_name=current_user.name,
            user_email=current_user.email,
            user_profile_pic=current_user.profile_pic,
            videos=video,

        )
    else:
        return render_template("login.html")

# Login


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri = request.base_url + "/callback",
        # redirect_uri = "/login/callback",
        scope=["openid", "email", "profile"],
    )
    print(request.base_url)
    return redirect(request_uri)


# Login Callback
@app.route("/login/callback", methods=['GET', 'POST'])
def callback():
    print("hello")
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    result = "<p>code: " + code + "</p>"

    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response = request.url,

        redirect_url = domain_name + "/login/callback",
        code = code,
    )
    token_response = requests.post(
        token_url,
        headers = headers,
        data = body,
        auth = (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    result = result + "<p>token_response: " + token_response.text + "</p>"

    # return result

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in your db with the information provided
    # by Google
    user = User(id_=unique_id, name = users_name,
                email = users_email, profile_pic = picture)

    # Doesn't exist? Add it to the database.
    if not User.get(unique_id):
        User.create(unique_id, users_name, users_email, picture)

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for("index"))


# Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/pred_spinrate/<video_path>')
def pred_spinrates(id, video_id, video_path, fps):
    # print(f"\n\n\n1. {fps}")
    result = pred_spinrate.delay(
        id=id, video_id=video_id, video_path=video_path, fps = fps)
    # ball_to_line_img = cutball(video_path)
    # pred_spinrate = pred(ball_to_line_img)
    return result


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    print("**")
    print("uploading data...\n")
    print("server accept mime: ", request.accept_mimetypes)  # /*
    print("client send mime: ", request.mimetype)  # video/quicktime
    # print("data {} bytes".format(len(request.data)))
    # print(type(request.data))

    fps = int(request.values.get('fps'))
    print(fps)

    if 'video' not in request.files:
        return redirect(request.url)

    file = request.files['video']
    if file.filename == '':
        return redirect(request.url)

    if file and allowed_file(file.filename):
        global upload_count
        upload_count += 1

        origin_filename = secure_filename(file.filename)
        # print(origin_filename)
        filename = str(upload_count)

        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename + ".avi"))

        time = datetime.now()
        upload_time = time.strftime('%Y-%m-%d %H:%M:%S')

        # add_upload_video(origin_filename, app.config['UPLOAD_FOLDER'] + filename + ".avi", upload_time, current_user.id)

        # spinrate = pred_spinrate(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # spinrate = 1832.6
        # data_return = {"RPM": int(spinrate)}

        # if not Video.get(current_user.id):
        Video.create(upload_count, current_user.id, origin_filename,
                     filename + ".avi", upload_time, "", "")
        video_path = os.path.join(
            app.config['UPLOAD_FOLDER'], filename + ".avi")
        result = pred_spinrates(current_user.id, upload_count, video_path, fps)
        tasks.append(result.id)

        # # result = pred_spinrate.delay(video_path)
        # if result.successful():
        #     print("Successful")
        #     result_value = result.get()
        #     print("任務結果:", result_value)
        # elif result.failed():
        #     print("fail")

        return redirect(url_for("index"))

    else:
        return redirect(url_for("index"))

# @app.route('/file/upload_video/<filename>', methods=['GET', 'POST'])
# def download(filename):
#     # filename = os.path.basename(filepath)
#     uploads_folder = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#     return send_from_directory(directory=uploads_folder, filename=filename)


@app.route('/file/upload_video/<filename>', methods=['GET', 'POST'])
def download(filename):
    uploads_folder = "C:/Users/UserPC/Desktop/baseball-speed-estimation-service-development/file/upload_video/"
    return send_from_directory(directory = uploads_folder, path = filename)


if __name__ == "__main__":
    # app.run(ssl_context=('C:\\Certbot\\live\\baseballspin.hopto.org\\fullchain.pem', 'C:\\Certbot\\live\\baseballspin.hopto.org\\privkey.pem'),debug = True,host='0.0.0.0',port= 5000)
    # app.run(ssl_context=('C:\\Certbot\\live\\basball.homelab.tw\\fullchain1.pem', 'C:\\Certbot\\live\\basball.homelab.tw\\privkey1.pem'),debug = True,host='0.0.0.0',port= 443)

    app.run(debug = True,host='0.0.0.0',port=443)
