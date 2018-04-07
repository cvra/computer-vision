import logging
import sys
from time import gmtime, strftime

import picamera
import picamera.array

from planReader.planReader import planReader


plan = planReader(config_path='conf.yaml',
                  config_color='colors.yaml', debug=False)

camera = picamera.PiCamera()
camera.vflip = True
camera.hflip = True
camera.resolution = (3280//2, 2464//2)

logging.info('{}: Start'.format(strftime("%a, %d %b %Y %H:%M:%S", gmtime())))

while(True):
    try:
        stream = picamera.array.PiRGBArray(camera)
        logging.info('{}: Grab Image'.format(strftime("%a, %d %b %Y %H:%M:%S", gmtime())))
        camera.capture(stream, format='rgb', use_video_port=True)

        logging.info('{}: Load Image'.format(strftime("%a, %d %b %Y %H:%M:%S", gmtime())))
        im = stream.array

        logging.info('{}: Process Image'.format(strftime("%a, %d %b %Y %H:%M:%S", gmtime())))
        color_plan = plan.process(im)

        logging.info('{}: Output {}'.format(strftime("%a, %d %b %Y %H:%M:%S", gmtime()), color_plan))
    except KeyboardInterrupt:
        logging.info('Exiting program after Ctrl-C')
        sys.exit()
