import time
import picamera
import picamera.array

from time import gmtime, strftime
from planReader.planReader import planReader


plan = planReader(config_path='conf.yaml',
                  config_color='colors.yaml', debug=False)

with picamera.PiCamera() as camera:
    camera.vflip = True
    camera.hflip = True
    camera.resolution = (3280//2, 2464//2)

    print('{}: Start'.format(strftime("%a, %d %b %Y %H:%M:%S",
                                      gmtime())))

    while(True):
        with picamera.array.PiRGBArray(camera) as stream:
            print('{}: Grab Image'.format(
                strftime("%a, %d %b %Y %H:%M:%S", gmtime())))
            camera.capture(stream, format='rgb', use_video_port=True)

            print('{}: Load Image'.format(
                strftime("%a, %d %b %Y %H:%M:%S", gmtime())))
            im = stream.array

            print('{}: Process Image'.format(
                strftime("%a, %d %b %Y %H:%M:%S", gmtime())))
            color_plan = plan.process(im)

            print('{}: Output {}'.format(
                strftime("%a, %d %b %Y %H:%M:%S", gmtime()), color_plan))
