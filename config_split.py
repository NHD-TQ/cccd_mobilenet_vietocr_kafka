import io
import os
import scipy.misc
import numpy as np
import six
import time
import glob
from IPython.display import display

from six import BytesIO

import matplotlib
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import cv2

import tensorflow as tf
from object_detection.utils import ops as utils_ops
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

#Load model
tf.keras.backend.clear_session()
# model = tf.saved_model.load("/content/gdrive/MyDrive/project_cccn/export_10-5/export_lan2/saved_model")
import cv2
import numpy as np

def run_inference_for_single_image(model, image):

  image = np.asarray(image)
  input_tensor = tf.convert_to_tensor(image)
  input_tensor = input_tensor[tf.newaxis,...]

  model_fn = model.signatures['serving_default']
  output_dict = model_fn(input_tensor)

  num_detections = int(output_dict.pop('num_detections'))
  output_dict = {key:value[0, :num_detections].numpy()
                 for key,value in output_dict.items()}
  output_dict['num_detections'] = num_detections
  output_dict['detection_classes'] = output_dict['detection_classes'].astype(np.int64)

  if 'detection_masks' in output_dict:
    detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
              output_dict['detection_masks'], output_dict['detection_boxes'],
               image.shape[0], image.shape[1])
    detection_masks_reframed = tf.cast(detection_masks_reframed > 0.5,
                                       tf.uint8)
    output_dict['detection_masks_reframed'] = detection_masks_reframed.numpy()

  return output_dict

def load_image_into_numpy_array(path):
  img_data = tf.io.gfile.GFile(path, 'rb').read()
  image = Image.open(BytesIO(img_data))
  (im_width, im_height) = image.size
  return np.array(image.getdata()).reshape(
      (im_height, im_width, 3)).astype(np.uint8)

def get_and_save_frame(box_class, box_score, box_coordinates, image, i):
    # Lấy ra các tọa độ: Trên, dưới, phải, trái
    image = image
    img_width, img_height = image.size
    a, b, c, d = box_coordinates[0], box_coordinates[1], box_coordinates[2], box_coordinates[3]
    (left, right, top, bottom) = (d * img_width, b * img_width, c * img_height, a * img_height)

    # Cắt ra các box và lưu vào thư mục

    # Đưa từ Pillow to Cv2
    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    source_points = np.float32([[right, bottom], [left, bottom], [left, top], [right, top]])
    dest_points = np.float32([[0, 0], [100, 0], [100, 30], [0, 30]])
    M = cv2.getPerspectiveTransform(source_points, dest_points)
    dst = cv2.warpPerspective(img, M, (100, 30))
    img_save = Image.fromarray(dst)
    img_save.save("C:\\Users\\admin\\OneDrive - ptit.edu.vn\\Desktop\\cccd_final\\frame_detected\\{0}_{1}.jpg".format(box_class, i))

