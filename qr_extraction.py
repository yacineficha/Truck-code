from glob import glob
from post_office import office
from gps import GPS
from qr_utils import *
from data_writer import data_writer
from qr_classes import Compactor_Monitor, Bin_Monitor
from datetime import datetime
import os
import itertools
import collections
from time import time, sleep
from class_canny import *
from threading import Thread
import cv2
import numpy as np
TEST = False

# To perform tests locally without the GPS / 4G switch the TEST to true also set use_camera to false in main function bellow & follow instructions there


if TEST:
    from gps_dummy import GPS


if TEST:
    from post_office_dummy import office


def extract(vid_name, output_dir, gps=None):
    sleep(1)
    f = open(output_dir+'/logs.txt', 'a')
    f.write(
        f"Start execution was at {datetime.today().strftime('%Y-%m-%d-%H:%M:%S')}"+'\n')
    f.close()
    print('start working on ', vid_name, ' saving in ', output_dir)
    prev_frame = None
    prev_gray = None
    Bin_M = Bin_Monitor()
    Compactor_M = Compactor_Monitor(save=output_dir + '/')

    # Capture video from camera
    # cap = cv2.VideoCapture(0)

    # Capture video from file
    cap = cv2.VideoCapture(vid_name)

    start_f = get_frame_start(output_dir)
    Compactor_M.frame_n = start_f
    post_office = office(output_dir)
    data_write = data_writer(output_dir, gps.lat, gps.lon, office=post_office)
    frame_nb = 0
    moves = 0
    stops = 0
    appears = 0
    first_ok = False
    lc = local_sim()
    error_flag = False
    start_record = 0

    # we take 30 frames, out of 600
    stop_record = 300
    process_fps = 3
    apprs = 0
    disapprs = 0
    possible_move = False
    frames_list = []
    bin_state = []
    while(cap.isOpened()):

        var = time()
        # Capture frame-by-frame
        ret, frame = cap.read()
        if ret == False:
            if error_flag:
                continue
            f = open(output_dir+'/logs.txt', 'a')
            f.write(
                f"Problem with the camera at {datetime.today().strftime('%Y-%m-%d-%H:%M:%S')}"+'\n')
            f.close()
            error_flag = True
            continue
        error_flag = False

        if frame_nb % process_fps != 0:
            frames_list.append(frame)
            frame_nb += 1
            continue
        if len(frames_list) == 0:
            frame_nb += 1
            continue
        sharps = [sharpness(f) for f in frames_list]
        frame_idx = np.argmax(sharps)
        frame = frames_list[frame_idx]
        frames_list = []
        h, w = frame.shape[0:2]

        # bar.next()

        # check for the existence of bin using the compactness index
        bin_ = lc.compactness(frame)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        gray = cv2.resize(gray, (256, 256))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        flow_gray = gray[:50, ...]
        curr_img = gray.copy()

        frame_nb += 1

        if prev_frame is None:
            prev_frame = curr_img
            prev_gray = flow_gray
            continue

        # detect new coming trash
        flow = cv2.calcOpticalFlowFarneback(prev_gray, flow_gray,
                                            None,
                                            0.5, 3, 15, 3, 5, 1.2, 0)
        yflow = flow[..., 0]
        pos = len(yflow[yflow >= 2])
        neg = len(yflow[yflow <= -2])

        # state vector to evalute the state of the scene (existance of compactor or bin)
        possible_move = pos > 100 or neg > 100 or bin_ > 25
        Bin_M.moving_flags.appendleft(possible_move)

        #compact2 = cv2.countNonZero(frame1[int(frame1.shape[0] * 0.66) :, ... ])

        sus_moves = sum(list(Bin_M.moving_flags)[:4]) > 2 or possible_move
        if sum(list(Bin_M.moving_flags)[:10]) > 7:
            Bin_M.appeared = True
            apprs += 1
            disapprs = 0
            if len(bin_state) == 0:
                bin_state = [1]
            elif bin_state[-1] == 0:
                bin_state.append(1)

        else:
            disapprs += 1

        if disapprs > 10:
            if len(bin_state) == 1 and bin_state[0] == 1:
                bin_state.append(0)
        Compactor_M.frame = frame

        if len(bin_state) == 1:
            if start_record == 0:
                start_record += 1
                #data_write.save_best(Compactor_M ,Bin_M, gps)

        if start_record > stop_record or len(bin_state) == 3:
            start_record = 0
            Bin_M.appeared = False
            Compactor_M.done_f = True
            data_write.rdy_commit = True
            disapprs = 0
            apprs = 0
            bin_state = []
            data_write = data_writer(
                output_dir, gps.lat, gps.lon, office=post_office)

        if start_record >= 1:

            if (start_record > 30 and disapprs > 20):
                #print(possible_move, sus_moves, Bin_M.moving_flags, bin_state)

                data_write.save_best(Compactor_M, not sus_moves)

            if start_record < 30:
                data_write.save_best(Compactor_M,)
            start_record += 1

        #print(time() - var)

        Compactor_M.frame_n += 1

        prev_frame = curr_img
        prev_gray = flow_gray

        """if cv2.waitKey(1) & 0xFF == ord('q'):

            exit()"""

        total_time = time() - var
        frame_nb += 1
    f = open(output_dir+'/logs.txt', 'a')
    f.write(
        f"End execution was at {datetime.today().strftime('%Y-%m-%d-%H:%M:%S')}"+'\n')
    f.close()
    data_write.save_best(Compactor_M)
    # When everything done, release the capture
    cap.release()

    cv2.destroyAllWindows()


def get_local_outputdir():

    if TEST:
        return './data/'
    temp = glob('/home/*')
    temp = [f for f in temp if 'root' not in f]
    if len(temp) == 0:
        return '/home/ficha/data/'
    path = temp[0]+'/'
    if not os.path.exists(path+'data'):
        os.makedirs(path+'data/')
    return path+'data/'


def get_outputdir():
    #res = os.listdir('/media/ficha')
    #res = [r for r in res if 'L4T' not in r]
    return get_local_outputdir()

    """if len(res) == 1:
        path = '/media/ficha/'+res[0]+'/data/'
        if not os.path.exists(path):
            try:
                os.makedirs(path)
                return path
            except:
                print('Failed creating the file')
                return get_local_outputdir() 
        return path
        
    return '/home/ficha/data'"""


def main(videos_path, formats='*.h264', output_dir='test', videos_list=None, use_camera=False, gps=None):
    from glob import glob

    if videos_list is None:
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

    print(data)
    gps = GPS()
    try:
        if use_camera:
            #m='nvarguscamerasrc ! video/x-raw(memory:NVMM), width=3840, height=2160, format=(string)NV12, framerate=(fraction)30/1 ! nvvidconv ! video/x-raw, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink'
            #m = "nvarguscamerasrc sensor_id=0 wbmode=0 awblock=true gainrange=\"8 8\" ispdigitalgainrange=\"4 4\" exposuretimerange=\"5000000 5000000\" aelock=true ! video/x-raw(memory:NVMM), width=3840, height=2160,format=(string)NV12, framerate=(fraction)30/1 ! nvvidconv ! video/x-raw, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink"
            #m = "nvarguscamerasrc sensor_id=0 wbmode=0 awblock=true  ispdigitalgainrange=\"8 8\" exposuretimerange=\"30000 30000\" aelock=false ! video/x-raw(memory:NVMM), width=3840, height=2160,format=(string)NV12, framerate=(fraction)30/1 ! nvvidconv ! video/x-raw, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink"
            m = 'nvarguscamerasrc exposuretimerange=\"11000000  210000000\" gainrange=\"16 18\" ! video/x-raw(memory:NVMM), width=1920, height=1080, format=(string)NV12, framerate=(fraction)30/1 ! nvvidconv  ! video/x-raw, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink'

            #m = '69.h264'
            output_dir = get_outputdir()
            extract(m, output_dir, gps)
        else:

            # If you want perform local test you better set use_camera to falsee and either populate the video_list input or the code will detect videos on the same folder
            for f, o in data:
                i = get_outputdir()
                extract(f, i, gps)
    except Exception as e:
        print(e)
        print('Exit code 0')
    finally:
        gps.stop = True
        print('GPS stopped')


if __name__ == '__main__':
    main(videos_path='./', use_camera=True)
