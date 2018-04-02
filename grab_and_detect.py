import cv2
import time
import picamera

from time import gmtime, strftime
from planReader.planReader import planReader

camera = picamera.PiCamera()
camera.vflip = True
camera.hflip = True
camera.resolution = (3280//2, 2464//2)

plan = planReader(config_path='conf.yaml',
                  config_color='colors.yaml', debug=False)

while(1):
    print('{}: Start'.format(strftime("%a, %d %b %Y %H:%M:%S", gmtime())))
    print('{}: Grab Image'.format(strftime("%a, %d %b %Y %H:%M:%S", gmtime())))
    name = strftime('out.png')
    camera.capture(name, format='png')

    print('{}: Load Image'.format(strftime("%a, %d %b %Y %H:%M:%S", gmtime())))
    im = cv2.imread(name, cv2.IMREAD_COLOR)
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    print('{}: Process Image'.format(strftime("%a, %d %b %Y %H:%M:%S", gmtime())))
    res = plan.process(im)
    print('{}: Output {}'.format(strftime("%a, %d %b %Y %H:%M:%S", gmtime()), res))
    time.sleep(5)
