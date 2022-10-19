import numpy as np
import cv2
import os

DETECTION_TYPE = "stripes"


if DETECTION_TYPE == 'stripes':
    from stripes_detection import aruco_code_detection
else:
    from aruco_detction import aruco_code_detection
    
def get_frame_start(path):
    from glob import glob

    c = glob(path+'/*.json')
    if len(c) == 0:
        return 0
    c = [i.split('/')[-1].split('\\')[-1] for i in c]
    c = sorted([int(i.split('.')[0]) for i in c])
    
    return np.max(c)


def detect_compactor(Compactor_M, frame, curr_img, first_ok):
        return aruco_code_detection(Compactor_M, frame, curr_img, first_ok)


def create_output_folder(path):
    try:
        os.mkdir(path)
        return True
    except OSError:
        return False
