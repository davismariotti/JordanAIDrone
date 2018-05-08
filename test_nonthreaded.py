"""
Demo the trick flying for the python interface
"""

from pyparrot import Mambo
import cv2


class MamboCamera:
    def __init__(self, feed):
        self.feed = feed
        self.capture = None

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


# you will need to change this to the address of YOUR mambo
mamboAddr = "e0:14:d0:63:3d:d0"
mamboRTSP = "rtsp://192.168.99.1/media/stream2"

# make my mambo object
# remember to set True/False for the wifi depending on if you are using the wifi or the BLE to connect
mambo = Mambo.Mambo(mamboAddr, use_wifi=True)

print("trying to connect")
success = mambo.connect(num_retries=3)
print("connected: %s" % success)

if success:
    # get the state information
    print("sleeping")
    mambo.smart_sleep(1)
    mambo.ask_for_state_update()
    mambo.safe_takeoff(5)
    mambo.smart_sleep(1)

    if mambo.sensors.flying_state != "emergency":
        print("flying state is %s" % mambo.sensors.flying_state)

        camera = MamboCamera(mamboRTSP)

        camera.connect()
        count = 0
        try:
            while camera.is_running():

                print(count)
                camera.get_frame()
                count += 1
        except KeyboardInterrupt:
            print('Shutting down')

        camera.disconnect()

        print('landing')
        mambo.safe_land(5)

    print("disconnect")
    mambo.disconnect()
