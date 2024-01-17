import matplotlib.pyplot as plt
from PIL import Image

from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg

def process_ocr(image):
    config = Cfg.load_config_from_name('vgg_transformer')
    config['cnn']['pretrained']=False
    config['device'] = 'cpu'
    detector = Predictor(config)

    # img = 'C:\\Users\\admin\\OneDrive - ptit.edu.vn\\Desktop\\cccd_final\\frame_detected\\4.jpg'
    img = image
    # plt.imshow(img)
    s = detector.predict(img)
    return s