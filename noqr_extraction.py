import numpy as np
import cv2
from threading import Thread
from class_canny import *
from time import time
import collections
import itertools
from noqr_utils import *
from noqr_classes import Compactor_Monitor, Bin_Monitor, data_writer


def extract(vid_name, output_dir) :
    print('start working on ', vid_name,' saving in ', output_dir)
    patch_n = 0

    Bin_M = Bin_Monitor()
    Compactor_M = Compactor_Monitor(save = output_dir + '/')   
    data_write = data_writer() 
    # Capture video from camera
    # cap = cv2.VideoCapture(0)

    # Capture video from file
    cap = cv2.VideoCapture( vid_name )
    threshold_com = 30

    moves = 0
    stops = 0
    appears = 0
    prev_frame = None
    prev_gray = None
    lc = local_sim()
    while(cap.isOpened()):
        # Capture frame-by-frame
        ret, frame = cap.read()
        width,height,_ = frame.shape
        if not ret :
            break

        bin_ = lc.compactor_exist(frame)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, (256, 256))
        curr_gray = gray[:50,...]
        curr_img = gray.copy()
        gray = gray[int(gray.shape[0]*0.3): ,...]



        compactor_y = template_matching(gray)
    


        if prev_frame is None :
            prev_frame = curr_img
            prev_gray = curr_gray
            continue

        pos_flow, neg_flow = calculate_bin_flow(prev_gray, curr_gray)




        #state vector to evalute the state of the scene (existance of compactor or bin)
        Bin_M.moving_flags.appendleft(pos_flow > 200 or neg_flow > 200 or bin_> 25)

        Compactor_M.moving_flags.appendleft (compactor_y > threshold_com)
        



        moving_pixels_total, moving_pixels_compactor = moving_pixels(curr_img, prev_frame)




        if sum(list(Bin_M.moving_flags)[:10]) > 7 :  
            Bin_M.appeared = True

        
        if Bin_M.moving_flags[0] : 
            moves +=1
        else :
            moves = 0

        if appears > 5 :
            Compactor_M.reappeared = True
        if stops > 5 : 
            Compactor_M.disappeared = True

        if not Compactor_M.moving_flags[0] : 
            stops +=1
        else :
            stops = 0
            if Compactor_M.disappeared :
                appears +=1
            else :
                appears = 0
        if Compactor_M.reappeared :
            data_write.save_best(Compactor_M ,Bin_M)

        if Bin_M.isIN_Scene() :
            if Bin_M.first_iterations :
                Bin_M.first_iterations = False
            if Bin_M.appeared :
                data_write.save_best(Compactor_M ,Bin_M)

            Compactor_M.disappeared = False
            Compactor_M.t = 0
            Compactor_M.reappeared = False

                
        else :
            
            if not  Compactor_M.isIN_Scene() and (Bin_M.appeared or Bin_M.first_iterations): 
                data_write.update_frame(Compactor_M, frame, compactor_y, moving_pixels_compactor,Bin_M.first_iterations)


  
        Compactor_M.frame_n += 1
        cv2.imshow('s',curr_img)


        prev_frame = curr_img
        prev_gray = curr_gray
        if cv2.waitKey(10) & 0xFF == ord('q'):
            exit()

    # When everything done, release the capture
    cap.release()

    cv2.destroyAllWindows()


def main(videos_path, formats = '*.h264', output_dir = 'data/', videos_list = None, use_camera = False):
    from glob import glob

    if videos_list is None :
        files = glob(videos_path+formats)
    else:
        files = videos_list
    data = []
    for f in files:
        vid_name = f.split('\\')[-1]
        vid_name = vid_name.split('/')[-1]
        vid_name = vid_name.split('.')[0]
        
        if vid_name != '':
            data.append((f, output_dir+'/'))
            #create_output_folder(data[-1][1])
    print(data)

    for f, o in data :
        extract(f, o)

