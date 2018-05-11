import cv2
import numpy as np
import time
from keras.preprocessing import image


def main_code():
    image_filename = "rec_frame_13_32_04_782814.jpg"

    kImg = image.load_img(image_filename, target_size=(150, 150))
    # image.
    kX = image.img_to_array(kImg)
    kX = np.expand_dims(kX, axis=0)
    cX = cv2.imread(image_filename, cv2.IMREAD_COLOR)
    cX = cv2.resize(cX, dsize=(150, 150), interpolation=cv2.INTER_CUBIC)
    cX = np.expand_dims(cX, axis=0)

start = time.time()
main_code()
print(time.time() - start)
