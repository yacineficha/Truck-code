
#MEASUREMENT = "SSIM"
MEASUREMENT = "MSE"

from collections import deque
from tokenize import Triple
import numpy as np
import cv2
import base64
import json
from datetime import datetime

#from post_office_dummy import office
from post_office import office
import threading
if MEASUREMENT == "SSIM":
    import pytorch_ssim
    import torch
    from torch.autograd import Variable
import queue




class data_writer(object):

    def __init__(self, path, lat, lon, office):
        self.post_office = office
        self.path = None
        self.n = -1
        self.writer = None
        if MEASUREMENT == 'SSIM':
            self.ssim_loss = pytorch_ssim.SSIM(window_size = 11)
        self.queue = queue.Queue()
        self.work = True
        self.rdy_commit = False
        self.img_lon = lon
        self.img_lat = lat
        self.thread = threading.Thread(target=self.run, args=())
        self.thread.daemon = True
        self.thread.start()  



    def run(self):
        while self.work:
            try:
                frame = self.queue.get(timeout=1)
                if self.writer is None:
                    continue
                self.writer.write(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            except:
                pass
            finally:
                if self.rdy_commit :
                    self.commit()
                    break
    #update the frame that will be saved
    def update_frame(self, Compactor_M, frame, m_pixels, first, gps):
        pass

    def create_writer(self, path, n, fps = 10):
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        self.writer = cv2.VideoWriter(f'{path}/{n}.mp4', fourcc, fps, (self.w, self.h))
        #self.writer = writer(path, n, ) 
        #self.writer = imageio.get_writer(f'{path}/{n}.gif', mode='I', )




    def reinit_gps(self):
        self.img_lon = 0
        self.img_lat = 0
    

    def warmup(self):
        
        img1 = Variable(torch.rand(1, 3, 32, 64))
        img2 = Variable(torch.rand(1, 3, 32, 64))
        if torch.cuda.is_available():
            img1 = img1.cuda()
            img2 = img2.cuda()
        self.ssim_loss(img1, img2)

    def SSIM(self, frame1, frame2, threshold = 0.6, device ='cuda:0'):
        img1 = torch.from_numpy(np.rollaxis(frame1, 2)).float().unsqueeze(0).to(device)
        img2 = torch.from_numpy(np.rollaxis(frame2, 2)).float().unsqueeze(0).to(device)
        return self.ssim_loss(img1, img2) > threshold

    def MSE(self, frame1, frame2, threhold = 30):

        temp = cv2.absdiff(frame1, frame2)
        temp[temp < threhold] = 0

        return np.count_nonzero(temp) < frame1.shape[0]*frame1.shape[1]*0.5

    def measure_similariy(self, frame1, frame2):
        if MEASUREMENT == 'SSIM':
            return self.SSIM(frame1, frame2).cpu().numpy()
        if MEASUREMENT  == 'MSE':
            return self.MSE(frame1, frame2)
        return False
    
    def compare_images(self, Compactor):
        #return True if similair, False otherwise
        if Compactor.last_save is None:
            return False
        temp_frame = cv2.resize(Compactor.frame, (64, 32))
        ssim =  self.measure_similariy(Compactor.last_save, temp_frame)
        return ssim


    def save_data(self, Compactor_M, n, frame, path):  
        self.h, self.w = frame.shape[:2]
        if self.writer is None:
            self.create_writer(path, n)
        Compactor_M.last_save = cv2.resize(frame, (64, 32))
        self.queue.put(frame.copy())
        if self.path is None:
            self.path = path
            self.n = n



    def commit(self):
         
            if self.path is None or self.writer is None:
                self.writer = None
                return False

            self.writer.release()
            self.writer = None
            
            if self.post_office.COLLECTION_TOKEN is None:
                collectID = 'ERROR'
            else:
                collectID = self.post_office.COLLECTION_TOKEN

            dict = {
                    'fpath': f'{self.path}/{self.n}.mp4',
                    'time_stamp' : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'latitude' : self.img_lat,
                    'longitude' : self.img_lon,
                    'CollectID' : collectID
                    }
            with open(f'{self.path}/{self.n}.json', 'w') as outfile:
                json.dump(dict, outfile, ensure_ascii=False, indent=4)

            self.post_office.push_data(f'{self.path}/{self.n}.json')
            self.path = None
            self.rdy_commit = False
            return True

    #save the 'best' frame
    def save_best(self, Compactor_M,  save_flag = True):
        if not save_flag:
            return
        if Compactor_M.frame is not None: 
            if Compactor_M.frame_n - Compactor_M.frame_save < 1 :
                Compactor_M.frame = None
                return

            
            #cv2.imwrite(Compactor_M.path_save+str(Compactor_M.frame_n)+'_1.png', Compactor_M.frame)
            #self.encode_data(Compactor_M.frame, gps, Compactor_M.frame_n, Compactor_M.path_save)
            compare_flag = not self.compare_images(Compactor_M)
            if compare_flag or Compactor_M.first_save < 4:
                if Compactor_M.first_save >= 4:
                    Compactor_M.first_save = 0
                frame = Compactor_M.frame
                self.save_data(Compactor_M, Compactor_M.frame_n, frame, Compactor_M.path_save)
                Compactor_M.first_save+=1
            Compactor_M.id += 1 
            Compactor_M.frame_save = Compactor_M.frame_n
