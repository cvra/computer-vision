import logging
import sys
from time import gmtime, strftime

import picamera
import picamera.array
import serial

from error_correction import error_correction
from planReader.planReader import planReader

def time_str():
    return strftime("%a, %d %b %Y %H:%M:%S", gmtime())

VALID_COLORS = {'Black':'K', 'Yellow':'Y', 'Orange':'O', 'Blue':'B', 'Green':'G'}

logging.basicConfig(level=logging.INFO)

def main():
    plan = planReader(config_path='conf.yaml',
                      config_color='colors.yaml', debug=False)

    ser = serial.Serial('/dev/serial0', 19200)
    logging.info('Serial port {} ready for streaming results'.format(ser.name))

    camera = picamera.PiCamera()
    camera.vflip = True
    camera.hflip = True
    camera.resolution = (3280//2, 2464//2)

    logging.info('{}: Start'.format(time_str()))

    while(True):
        try:
            stream = picamera.array.PiRGBArray(camera)
            logging.info('{}: Grab Image'.format(time_str()))
            camera.capture(stream, format='rgb', use_video_port=True)

            logging.info('{}: Load Image'.format(time_str()))
            im = stream.array

            logging.info('{}: Process Image'.format(time_str()))
            color_plan = plan.process(im)

            logging.info('{}: Output {}'.format(time_str(), color_plan))

            if len(color_plan) == 3:
                sequences, distance = error_correction(color_plan)
                logging.info('{}: Closest valid sequence {} that was {} color away from prediction'.format(time_str(), sequences[0], distance))

                compact_res = ''.join(VALID_COLORS[color] for color in sequences[0]) + '\n'
                ser.write(compact_res.encode())
                logging.info('UART stream: {}'.format(compact_res))
            else:
                logging.warning('Invalid color sequence detected {} does not contain exactly 3 colors'.format(color_plan))
        except KeyboardInterrupt:
            logging.info('Exiting program after Ctrl-C')
            ser.close()
            sys.exit()

if __name__ == '__main__':
    main()
