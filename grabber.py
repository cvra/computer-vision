#!/usr/bin/env python3
import time
import picamera
from time import gmtime, strftime
import uuid
import os

folder = uuid.uuid4().hex
os.mkdir(folder)

camera = picamera.PiCamera()
camera.vflip = True
camera.resolution = (3280//2, 2464//2)

while(1):
  name = os.path.join(folder, strftime('%Y%m%d_%H_%M_%S.png', gmtime()))
  camera.capture(name, format='png')
  time.sleep(5)
