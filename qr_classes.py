from collections import deque
from tokenize import Triple
import numpy as np
import cv2
import base64
import json
from datetime import datetime

from post_office_dummy import office
#from post_office import office
import threading

import queue


MEASUREMENT = "SSIM"
#MEASUREMENT = "MSE"


class writer(object):
    def __init__(self, path, n, format = 'jpg'):
        self.path = path
        self.n = n
        self.format = format
    def write(self, data):
        cv2.imwrite(f'{self.path}/{self.n}.{self.format}', data) 
        self.n += 1

class Compactor_Monitor(object):
    def __init__(self, id_im=0, save='test/'):
        self.frame = None
        self.id = id_im
        self.path_save = save
        self.reset_flags()
        self.reinit()
        self.frame_save = 0
        self.frame_n = 0
        self.f_done = False
        self.last_save = None
        self.first_save = 9999


    def reinit(self):
        self.frame = None
    def reset_flags(self):
        self.moving_flags =  deque([1]*5,maxlen=5)
    def InScene(self):
        return np.count_nonzero(self.moving_flags) > 0

class Bin_Monitor(object):
    def __init__(self):
        self.moving_flags = deque([0]*30, maxlen=30)
        self.first_iterations = True
        self.appeared = False

    def InScene(self):
        return (np.sum(self.moving_flags) > 8) or (sum(list(self.moving_flags)[:12]) > 0)
