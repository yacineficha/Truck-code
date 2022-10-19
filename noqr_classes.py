from collections import deque
import numpy as np
import cv2
from post_office import office
import datetime
import json
class Compactor_Monitor(object):
    def __init__(self, id_im = 0, save = 'test/'):
        self.id = id_im
        self.path_save = save
        self.frame_save = 0
        self.frame_n = 0
        self.disappeared = False
        self.reappeared = False
        self.t = 0
        self.f_done = False
        self.reinit()
        self.reset_flags()
        self.frame = None

    def reinit(self):
        self.moving_pixels = 999999
        self.compactor_pixels = 999999
        self.t = 0

    def reset_flags(self):
        self.moving_flags =  deque([1]*5,maxlen=5)

    def isIN_Scene(self):
        return np.count_nonzero(self.moving_flags) > 0



class Bin_Monitor(object):
    def __init__(self):
        self.moving_flags =  deque([0]*30,maxlen=30)
        self.first_iterations = True
        self.appeared = False


    def isIN_Scene(self):     
        return (np.sum(self.moving_flags) > 8 ) or (sum(list(self.moving_flags)[:12]) > 0)

class data_writer(object):

    def __init__(self, ):
        self.post_office = office()
        #update the frame that will be saved
    def update_frame(self, Compactor_M, frame,m, m_pixels, first):
        #print(m, self.moving_flags)

        if (m <= Compactor_M.compactor_pixels or m < 3) and (not Compactor_M.reappeared or first):
            
            Compactor_M.compactor_pixels = m
            if m_pixels == 0 :
                Compactor_M.t += 1



            if Compactor_M.t > 5  :

                Compactor_M.frame = frame
                #self.f_done = True
                Compactor_M.t = 0
                return True
        else :
            Compactor_M.t = Compactor_M.t - 1
            if Compactor_M.t < 0:
                Compactor_M.reinit()
        return False

    def save_data(self, frame, n, path):

        cv2.imwrite(f'{path}/{n}.png', frame)
        dict = {
                'fpath': f'{path}/{n}.png',
                'time_stamp' : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'latitude' : '0',
                'longitude' : '0'
               }
        with open(f'{path}/{n}.json', 'w') as outfile:
            json.dump(dict, outfile, ensure_ascii=False, indent=4)
        self.post_office.push_data(f'{path}/{n}.json')

    # save best frame
    def save_best(self, Compactor_M, Bin_M, gps):
        if Compactor_M.frame is not None: 
            if Compactor_M.frame_n - Compactor_M.frame_save < 10 :
                Compactor_M.frame = None
                return
            self.save_data(Compactor_M.frame, Compactor_M.frame_n, Compactor_M.path_save)
            Compactor_M.id += 1 
            Compactor_M.reinit()
            Compactor_M.reset_flags()
            Compactor_M.frame_save = Compactor_M.frame_n
            Compactor_M.f_done = False
            Bin_M.appeared = False
            Bin_M.first_iterations = False







