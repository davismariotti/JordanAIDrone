"""
Demo the trick flying for the python interface
"""

from Mambo import Mambo
import cv2
import os
import datetime
import numpy as np
from keras.models import load_model
# from keras.preprocessing import image
import time

class MamboCamera:
    def __init__(self, feed):
        self.feed = feed
        self.capture = None
        self.count = 0

    def connect(self):
        self.capture = cv2.VideoCapture(self.feed)
        print('camera connected')

    def disconnect(self):
        self.capture.release()
        cv2.destroyAllWindows()
        print('camera disconnected')

    def is_running(self):
        return self.capture.isOpened() and cv2.waitKey(33) != ord('q')

    def get_frame(self):
        if self.capture.isOpened():
            ret, frame = self.capture.read()
            if not ret:
                return False
            return frame
        else:
            return False

    def save_frame(self):
        frame = self.get_frame()
        file_name = "rec_frame_" + datetime.datetime.now().time().strftime('%H_%M_%S_%f') + ".jpg"
        cv2.imwrite(os.path.join('images/right', file_name), frame)
        self.count += 1


class MamboModel:
    def __init__(self, model_file):
        self.model_file = model_file
        self.model = load_model(self.model_file)

    def use(self, frame):
        img = cv2.resize(frame, dsize=(150, 150), interpolation=cv2.INTER_CUBIC)
        img = np.expand_dims(img, axis=0)
        return self.model.predict(img, verbose=1)[0]


mamboAddr = "e0:14:d0:63:3d:d0"
mamboRTSP = "rtsp://192.168.99.1/media/stream2"

# make my mambo object
# remember to set True/False for the wifi depending on if you are using the wifi or the BLE to connect
mambo = Mambo(mamboAddr, use_wifi=True)

print("trying to connect")
success = mambo.connect(num_retries=3)
print("connected: %s" % success)

if success:
    # get the state information
    print("sleeping")
    mambo.smart_sleep(1)
    mambo.ask_for_state_update()
    mambo.safe_takeoff(5)

    if mambo.sensors.flying_state != "emergency":
        print("flying state is %s" % mambo.sensors.flying_state)

        mambo.smart_sleep(1)

        try:
            camera = MamboCamera(mamboRTSP)
            print("Connecting to camera")
            camera.connect()
            print("Camera connected")
            print("Loading Model")
            model = MamboModel("first_model_full.h5")
            print("Model loaded")
            count = 0
            while camera.is_running():
                if count == 0:
                    print("Camera running")
                mambo.smart_sleep(0.25)
                print(count)
                start = time.time()
                fr = camera.get_frame()
                x = model.use(fr)
                print(x)
                count += 1
                print(time.time() - start)
        except KeyboardInterrupt:
            print('Shutting down')

        camera.disconnect()

        print('landing')
        mambo.safe_land(5)

    print("disconnect")
    mambo.disconnect()
