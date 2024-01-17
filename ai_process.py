from config_split import *
from ocr import *
import cv2
import os
from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg
import numpy as np

# Trích xuất xử lý xong frame ảnh thì xóa luôn để làm mới
def delete_files_in_directory(directory_path):
     files = os.listdir(directory_path)
     for file in files:
       file_path = os.path.join(directory_path, file)
       if os.path.isfile(file_path):
         os.remove(file_path)
     print("All files deleted successfully.")

# Khởi tạo các model gồm Mobilenet và OCR với Kafka
tf.keras.backend.clear_session()
model = tf.saved_model.load("saved_model")
# Ocr
config = Cfg.load_config_from_name('vgg_transformer')
config['cnn']['pretrained'] = False
config['device'] = 'cpu'
detector = Predictor(config)

import kafka_config
from kafka import KafkaConsumer
from kafka import KafkaProducer

# Model AI nhận hình ảnh về và xử lý
# khởi tạo consumer
topic_name = "img_from_user"
topic_name_producer = "resp_to_user"
c = KafkaConsumer(
    topic_name,
    bootstrap_servers = [kafka_config.kafka_ip],
    auto_offset_reset = 'latest',
    enable_auto_commit = True,
    fetch_max_bytes = 9000000,
    fetch_max_wait_ms = 10000
)

# processing
def process_image(image_np, image):
    category_index = label_map_util.create_category_index_from_labelmap("label_map.txt", use_display_name=True)
    # image_path = 'C:\\Users\\admin\\OneDrive - ptit.edu.vn\\Desktop\\cccd_final\\images\\img_6.jpg'
    # image_np = load_image_into_numpy_array(image_path)
    # print("Done load image ")
    image_np = cv2.resize(image_np, dsize=None, fx=1, fy=1)
    output_dict = run_inference_for_single_image(model, image_np)
    print("Done inference")
    # img = cv2.imread("C:\\Users\\admin\\OneDrive - ptit.edu.vn\\Desktop\\cccd_final\\images\\img_6.jpg", cv2.IMREAD_COLOR)
    vis_util.visualize_boxes_and_labels_on_image_array(
        image_np,
        output_dict['detection_boxes'],
        output_dict['detection_classes'],
        output_dict['detection_scores'],
        category_index,
        instance_masks=output_dict.get('detection_masks_reframed', None),
        use_normalized_coordinates=True,
        line_thickness=8)

    # Lấy ra các frame image đã detect được
    folder = "C:\\Users\\admin\\OneDrive - ptit.edu.vn\\Desktop\\cccd_final\\frame_detected"  # imahe
    delete_files_in_directory(folder)
    threshold = 0.52
    for i in range(100):
        if output_dict['detection_scores'][i] > 0.5:
            get_and_save_frame(output_dict['detection_classes'][i], output_dict['detection_scores'][i], output_dict['detection_boxes'][i], image, i)

    # Cho OCR vào để trả ra kết quả.
    images = []
    split_class = []
    for filename in os.listdir(folder):
        img = Image.open(os.path.join(folder, filename))
        split_class.append(filename[0])

        if img is not None:
            images.append(img)
    results = {"Id": None, "Họ và tên": None, "Ngày sinh": None, "Nguyên quán": None, "Thường trú": None}
    arr_string_results = ["", "", "", "", "", ""]
    # print(split_class)
    for i in range(len(split_class)):
        if split_class[i] == '1':
            arr_string_results[int(split_class[i])] = arr_string_results[int(split_class[i])] + detector.predict(images[i])
            # results(process_ocr(image))
        if split_class[i] == '2':
            arr_string_results[int(split_class[i])] = arr_string_results[int(split_class[i])] + detector.predict(images[i])
        if split_class[i] == '3':
            arr_string_results[int(split_class[i])] = arr_string_results[int(split_class[i])] + detector.predict(images[i])
        if split_class[i] == '4':
            arr_string_results[int(split_class[i])] = arr_string_results[int(split_class[i])] + " " + detector.predict(images[i])
        if split_class[i] == '5':
            arr_string_results[int(split_class[i])] = arr_string_results[int(split_class[i])] + " " + detector.predict(images[i])

    for i in range(1, 6, 1):
        if i == 1:
            results['Id'] = arr_string_results[i]
        if i == 2:
            results['Họ và tên'] = arr_string_results[i]
        if i == 3:
            results['Ngày sinh'] = arr_string_results[i]
        if i == 4:
            results['Nguyên quán'] = arr_string_results[i]
        if i == 5:
            results['Thường trú'] = arr_string_results[i]
    return results
    # p.send(topic_name_producer, results)

# Khởi tạo Producer
import json
def json_serializer(data):
    return json.dumps(data).encode('utf-8')
p = KafkaProducer(
    bootstrap_servers = [kafka_config.kafka_ip],
    # max_request_size = 9000000,
    value_serializer = json_serializer,
)

# conf = {'bootstrap.servers': 'pkc-abcd85.us-west-2.aws.confluent.cloud:9092',
#         'security.protocol': 'SASL_SSL',
#         'sasl.mechanism': 'PLAIN',
#         'sasl.username': '<CLUSTER_API_KEY>',
#         'sasl.password': '<CLUSTER_API_SECRET>',
#         'client.id': socket.gethostname()}



for message in c:
    img = message.value

    img = np.frombuffer(img, dtype=np.uint8)
    img_np = cv2.imdecode(img, cv2.IMREAD_COLOR)
    # cv2.imshow("img_from_user", img)
    # print(img)
    img = Image.fromarray(img_np)
    results = process_image(img_np, img)
    p.send(topic_name_producer, results)






