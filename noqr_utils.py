import numpy as np
import cv2
import os
from cv2 import aruco
aruco_dict = aruco.Dictionary_get(aruco.DICT_6X6_250)
parameters = aruco.DetectorParameters_create()

def compactor_exists(gray):

    corners, ids, rejectedImgPoints = aruco.detectMarkers(
        gray, aruco_dict, parameters=parameters)
    if len(corners) > 0:

        idss = np.array(ids).reshape(-1)
        idss = np.where(idss == 6)

        if len(idss[0]) == 0:
            idss = [[0]]

        return np.squeeze(corners[idss[0][0]]).astype('int')

    return None


def get_bbox(bbox):
    xmin = np.min(bbox[:, 0])
    ymin = np.min(bbox[:, 1])
    xmax = np.max(bbox[:, 0])
    ymax = np.max(bbox[:, 1])
    return xmin, ymin, xmax, ymax


def aruco_code_detection(Compactor_M, frame, curr_img, first_ok):

    if Compactor_M.marker is not None:
        ok, bbox = Compactor_M.tracker.update(frame)

        if ok:
            first_ok = True

            p1 = (int(bbox[0]), int(bbox[1]))

            rett = 256 - 20 - p1[1]
            if rett < -1:
                rett = 0

        else:
            rett = -1
            first_ok = False

    else:
        ok = False
        rett = -1
    if not ok:
        compactor_y = compactor_exists(curr_img)
        if compactor_y is not None:
            xmin, ymin, xmax, ymax = get_bbox(compactor_y)

            Compactor_M.marker = curr_img[ymin - 50:ymin+5, xmin:xmin+20]

            if not first_ok:
                Compactor_M.tracker = cv2.TrackerKCF_create()
                Compactor_M.tracker.init(frame, (xmin, ymin - 10, 20, 20))

            rett = 256 - ymin + 10

        else:
            rett = -1
    return rett, first_ok


def create_output_folder(path):
    try:
        os.mkdir(path)
        return True
    except OSError:
        return False

def template_matching(gray):

        # Perform match operations to detect the compactor, we use two different criterias to detect the compactor.
        res = cv2.matchTemplate(gray, template, cv2.TM_CCORR_NORMED)
        # Specify a threshold
        threshold = 0.98  
        # Store the coordinates of matched area in a numpy array
        loc = np.where( res > threshold)

        t = zip(*loc[::-1])
        t = np.array([f for f in t])

        if len(t)> 20 :
            compactor_y = int(np.median(t[:, 1]))
            compactor_y = gray.shape[0] - h_template - compactor_y
        else :
            compactor_y = -1
        return compactor_y


def calculate_bin_flow(prev_gray, curr_gray):
        flow = cv2.calcOpticalFlowFarneback(prev_gray, curr_gray,
                                    None,
                                    0.5, 3, 15, 3, 5, 1.2, 0)
        yflow = flow[..., 0]
        pos = len(yflow[yflow>= 1])
        neg = len(yflow[yflow<= -1])

        return pos, neg
def moving_pixels(curr_img,prev_frame):

        kernel = np.ones((3, 69), np.uint8)

        frame1 = cv2.absdiff(curr_img,prev_frame)

        frame1[frame1<5] = 0
        frame1[frame1>0] = 255

        moving_pixels_total = cv2.countNonZero(frame1)

        
        frame1 = cv2.morphologyEx(frame1, cv2.MORPH_OPEN, kernel)
        moving_pixels_compactor = cv2.countNonZero(frame1[frame1.shape[0] // 2 :, ... ])


        return moving_pixels_total, moving_pixels_compactor

def create_output_folder(path):
    try:
        os.mkdir(path)
        return True
    except OSError:
        return False

template = cv2.imread('temp.PNG',0)
#template2 = cv2.imread('Capture2.png',0)
template = cv2.resize(template, (200, 8))
#template2 = cv2.resize(template2, (230, 32))

# Store width and height of template in w and h
w_template, h_template = template.shape[::-1]
