import time
import picamera
from time import gmtime, strftime

camera = picamera.PiCamera()
camera.vflip = True
camera.resolution = (3280//2, 2464//2)

while(1):
  name = strftime('images/%Y%m%d_%H_%M_%S.png', gmtime())
  camera.capture(name, format='png')
  time.sleep(5)
