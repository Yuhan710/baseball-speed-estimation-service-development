FROM python:3.8.16

COPY . /app

WORKDIR /app
# 安裝依賴項

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install opencv-python-headless
RUN pip install tensorflow
RUN pip install waitress
# 運行應用程式
EXPOSE 8070
CMD [ "python", "routes.py" ]

          <!-- <td><a href="{{url_for('download', video[1]) }}" download="{{ video[0] }}">{{ video[0] }}</a></td> -->

          <!-- <td><a href="{{url_for('download', video[3]) }}" download="a.avi">下載</a></td> -->

