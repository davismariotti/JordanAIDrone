"""
Demo the trick flying for the python interface
"""

from Mambo import Mambo
import cv2
import os
import datetime
import numpy as np
from keras.models import load_model
import time
import operator
from threading import Thread
from queue import LifoQueue


class MamboCamera:
    def __init__(self, feed):
        self.feed = feed
        self.capture = None
        self.queue = LifoQueue()
        self.thread = Thread(target=self.start, args=())
        self.thread.daemon = True
        self.qsize = 0

    def connect(self):
        self.capture = cv2.VideoCapture(self.feed)
        print('camera connected')

    def start(self):
        while True:
            if self.capture.isOpened():
                ret, frame = self.capture.read()
                if ret:
                    self.queue.put(frame)

    def disconnect(self):
        self.capture.release()
        cv2.destroyAllWindows()
        print('camera disconnected')

    def is_running(self):
        return self.capture.isOpened() and cv2.waitKey(33) != ord('q')

    def get_frame(self):
        if self.queue.qsize() == 0:
            return None
        fr = self.queue.get()
        return fr

    def save_frame(self, location, frame):
        file_name = "rec_frame_" + datetime.datetime.now().time().strftime('%H_%M_%S_%f') + ".jpg"
        cv2.imwrite(os.path.join(location, file_name), frame)


class MamboModel:
    def __init__(self, model_file):
        self.model_file = model_file
        self.model = load_model(self.model_file)

    def use(self, frame):
        img = cv2.resize(frame, dsize=(150, 150), interpolation=cv2.INTER_CUBIC)
        img = np.expand_dims(img, axis=0)
        return self.model.predict(img, verbose=1)[0]


class Drone:
    def __init__(self, rtspaddr):
        self.rtspaddr = rtspaddr
        self.drone = Mambo("", use_wifi=True)
        print("trying to connect")
        self.success = self.drone.connect(num_retries=3)
        print("connected: %s" % self.success)

    def fly(self, takeoff=True):
        # get the state information
        print("sleeping")
        self.drone.smart_sleep(1)
        self.drone.ask_for_state_update()
        if takeoff:
            self.drone.safe_takeoff(5)
            self.drone.fly_direct(roll=0, pitch=0, yaw=0, vertical_movement=10, duration=1.5)

        if self.drone.sensors.flying_state != "emergency":
            print("flying state is %s" % self.drone.sensors.flying_state)

            self.drone.smart_sleep(1)

            camera = None

            try:
                camera = MamboCamera(self.rtspaddr)
                print("Connecting to camera")
                camera.connect()
                print("Camera connected")
                print("Starting camera thread")
                camera.thread.start()
                print("Camera thread started")
                print("Loading Model")
                model = MamboModel("first_model_full.h5")
                print("Model loaded")
                count = 0
                while camera.is_running():
                    if count == 0:
                        print("Camera running")
                    self.drone.smart_sleep(0.75)
                    print("Count: ", count)
                    start = time.time()

                    print("QUEUE SIZE: --------------------- ", camera.queue.qsize())
                    fr = camera.get_frame()
                    print("Frame: ", type(fr))
                    if fr is None:
                        continue
                    camera.save_frame('images/test', frame=fr)
                    x = model.use(fr)
                    print("Model output: ", x)
                    index = max(enumerate(x), key=operator.itemgetter(1))[0]
                    if x[0] == 0 and x[1] == 0 and x[2] == 0:
                        pass
                    elif index == 0:
                        self.drone.fly_direct(roll=0, pitch=10, yaw=-20, vertical_movement=0, duration=0.5)
                        print("LEFT")
                    elif index == 1:
                        self.drone.fly_direct(roll=0, pitch=10, yaw=20, vertical_movement=0, duration=0.5)
                        print("RIGHT")
                    elif index == 2:
                        self.drone.fly_direct(roll=0, pitch=10, yaw=0, vertical_movement=0, duration=0.5)
                        print("STRAIGHT")
                    print("Index: ", index)
                    count += 1
                    print("Time: ", time.time() - start)
            except KeyboardInterrupt:
                print('Shutting down')

                if camera is not None:
                    camera.disconnect()

            print('landing')
            self.drone.safe_land(5)

        print("disconnect")
        self.drone.disconnect()

    def trainfly(self):
        # get the state information
        print("sleeping")
        self.drone.smart_sleep(1)
        self.drone.ask_for_state_update()
        self.drone.safe_takeoff(5)

        if self.drone.sensors.flying_state != "emergency":
            print("flying state is %s" % self.drone.sensors.flying_state)

            self.drone.smart_sleep(1)

            camera = None

            try:
                camera = MamboCamera(self.rtspaddr)
                print("Connecting to camera")
                camera.connect()
                print("Camera connected")
                count = 0
                while camera.is_running():
                    if count == 0:
                        print("Camera running")
                        self.drone.smart_sleep(0.25)
                    print("Count:", count)
                    ret, fr = camera.capture.read()
                    if fr is not None:
                        camera.save_frame('images/test', frame=fr)
                    count += 1

            except KeyboardInterrupt:
                print('Shutting down')
                if camera is not None:
                    camera.disconnect()

            print('landing')
            self.drone.safe_land(5)

        print("disconnect")
        self.drone.disconnect()


print("Which mode would you like to use?")
print("1 - Training mode")
print("2 - Real mode")
print("3 - Camera test mode")
mode = input()
drone = Drone("rtsp://192.168.99.1/media/stream2")
if drone.success:
    if mode == "1":
        drone.trainfly()
    elif mode == "2":
        drone.fly()
    else:
        drone.fly(takeoff=False)
