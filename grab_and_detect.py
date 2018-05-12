import argparse
import logging
import os
import sys

import time
from time import gmtime, strftime
import uuid
import os
import cv2

import picamera
import picamera.array
import serial

from error_correction import error_correction
from planReader.planReader import planReader

def time_str():
    return strftime("%a, %d %b %Y %H:%M:%S", gmtime())

VALID_COLORS = {'Black':'K', 'Yellow':'Y', 'Orange':'O', 'Blue':'B', 'Green':'G'}

def parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('--port', '-p', help='Serial port the results are streamed to', default='/dev/serial0')
    parser.add_argument('--baudrate', '-b', type=int, help='Baudrate over serial port', default=19200)
    parser.add_argument('--logfile', '-l', help='Output log file')

    return parser.parse_args()

def main():
    args = parse_arguments()

    folder = os.path.join('/home/pi/computer-vision', uuid.uuid4().hex)
    os.mkdir(folder)

    if args.logfile:
        logging.basicConfig(filename=args.logfile, level=logging.INFO)
    else:
        logging.basicConfig(level=logging.INFO)

    ser = serial.Serial(args.port, args.baudrate)
    logging.info('Serial port {} ready for streaming results'.format(ser.name))

    camera = picamera.PiCamera()
    camera.vflip = True
    camera.hflip = True
    camera.resolution = (3280//2, 2464//2)

    current_dir = os.path.dirname(os.path.realpath(__file__))
    config_file = os.path.join(current_dir, 'conf.yaml')
    colors_file = os.path.join(current_dir, 'colors.yaml')
    plan = planReader(config_path=config_file,
                      config_color=colors_file, debug=False)

    logging.info('{}: Start'.format(time_str()))
    while(True):
        try:
            stream = picamera.array.PiRGBArray(camera)
            logging.info('{}: Grab Image'.format(time_str()))
            camera.capture(stream, format='rgb', use_video_port=True)
            im = stream.array

            logging.info('{}: Process Image'.format(time_str()))
            color_plan = plan.process(im)

            logging.info('{}: Output {}'.format(time_str(), color_plan))

            sequence, distance = error_correction(color_plan)
            
            logging.info('{}: Closest valid sequence {} that was {} color away from prediction'.format(time_str(), sequence, distance))

            if sequence:
                compact_res = '@' + ''.join(VALID_COLORS[color] for color in sequence) + '\n'
                ser.write(compact_res.encode())
                logging.info('UART stream: {}'.format(compact_res))
            else:
                logging.warning('Invalid color sequence detected {} does not contain exactly 3 colors'.format(color_plan))
        
            name = os.path.join(folder, strftime('%Y%m%d_%H_%M_%S.png', gmtime()))
            cv2.imwrite(name, cv2.cvtColor(im, cv2.COLOR_RGB2BGR))
        except KeyboardInterrupt:
            logging.info('Exiting program after Ctrl-C')
            ser.close()
            sys.exit()

if __name__ == '__main__':
    main()
