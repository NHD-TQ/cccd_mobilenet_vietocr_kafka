import io
# from run_test import *
import flask
from flask import Flask, render_template, request
from PIL import Image
# from run_test import *
from numpy import asarray
# from run_test import *
import json
from werkzeug.utils import secure_filename
import cv2
import os
import numpy as np
# Setup kafka
import kafka_config
from kafka import KafkaProducer
from kafka import KafkaConsumer
# Thư viện chuyển từ dạng bytes sang dictionary từ message kafka
from ast import literal_eval



topic_name_producer = "resp_to_user"
topic_name = "img_from_user"

p = KafkaProducer(
    bootstrap_servers = [kafka_config.kafka_ip],
    max_request_size = 9000000
)

# Nhận kết quả trả về từ model AI
c = KafkaConsumer(
    topic_name_producer,
    bootstrap_servers=[kafka_config.kafka_ip],
    auto_offset_reset='latest',
    enable_auto_commit=True,
    fetch_max_bytes=9000000,
    fetch_max_wait_ms=10000
)

app = Flask(__name__)


def delete_files_in_directory(directory_path):
    files = os.listdir(directory_path)
    for file in files:
        file_path = os.path.join(directory_path, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
    print("All files deleted successfully.")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    if request.method == 'POST':
        image = request.files['image'].read()
        # Save image user upload
        folder_image = "C:\\Users\\admin\OneDrive - ptit.edu.vn\\Desktop\\cccd_final\\static\\image_submited"
        delete_files_in_directory(folder_image)
        # image.save(secure_filename(image.filename))

        # Đọc ảnh user upload
        image = Image.open(io.BytesIO(image))
        image.save("C:\\Users\\admin\OneDrive - ptit.edu.vn\\Desktop\\cccd_final\\static\\image_submited\\image.jpg")
        # Chuyển ảnh thành dạng byte sau đó gửi về model AI xử lý
        img_cv2 = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        img_cv2 = cv2.resize(img_cv2, dsize=None, fx=1, fy=1)
        ret, buffer = cv2.imencode('.jpg', img_cv2)
        p.send(topic_name, buffer.tobytes())
        p.flush()
        print("Hình ảnh đã được gửi đến AI model")

        for message in c:
            results = message.value
            # return render_template('result.html', result=results)
            # Chuyển đổi từ dạng bytes (message bắn từ kafka thành dạng dictionary)
            results = literal_eval(results.decode('utf8'))
            return render_template("result.html", results=results)

        # results = process_image()
        # Convert image về dạng numpy
        np_img = asarray(image)
        #
        # # Đưa vào process with AI
        # results = process_image(np_img, image)
        # return render_template('result.html', result = results)
        # return render_template("result.html", results=results)







if __name__ == '__main__':
    app.run(debug=True)