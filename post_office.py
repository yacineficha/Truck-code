from threading import Thread
import queue
from time import sleep
import os
import json
import requests
from datetime import datetime
from glob import glob

from utils.encode_video_h264 import encode_video_h264

URL = "https://truck-staging.ew.r.appspot.com/collection/"
TRUCK_TOKEN = "EwVH1b08A9dOkPOGpzen"


class office(object):
    """docstring for office"""

    def __init__(self, path):
        self.queue = queue.Queue()
        self.work = True
        self.path = path
        self.TRUCK_TOKEN = self.get_TRUCK_TOKEN()
        self.init_collection()

        self.thread = Thread(target=self.send_loop, daemon=True)
        self.thread.start()

    def get_TRUCK_TOKEN(self):
        return TRUCK_TOKEN

    def init_collection(self):
        self.COLLECTION_TOKEN = get_token(self.path)

    def check_untreated_data(self):
        return len(glob(self.path+'*.json')) > 0

    def send_remaining_data(self):
        data = glob(self.path+'*.json')
        for d in data:
            try:
                self.send_request(d)
            except:
                continue

    def send_request(self, json_path):
        try:
            print(json_path)
            with open(json_path) as json_file:
                data = json.load(json_file)
        except:
            print('File not found')
            return
        fpath, save_time, lon, lat = data['fpath'], data['time_stamp'], data['longitude'], data['latitude']

        # encode video to h264 before sending it
        encoded_fpath = fpath.split(".mp4")[0] + "_encoded" + ".mp4"
        encode_video_h264(fpath, encoded_fpath)

        try:

            if int(lat) == 0 or int(lon) == 0:
                data = {
                    'timestamp': save_time,
                }
            else:
                data = {
                    'timestamp': save_time,
                    "longitude": lon,
                    "latitude": lat
                }

            if 'CollectID' in data:
                CollectID = data['CollectID']
            else:
                CollectID = 'ERROR'

            if CollectID == 'ERROR':
                CollectID = self.COLLECTION_TOKEN
            r = requests.post(
                f"{URL}{CollectID}/batch-video",
                headers={'Token': f"{self.TRUCK_TOKEN}"},
                files={
                    ('video', (encoded_fpath, open(encoded_fpath, 'rb'), 'video/mp4')),
                    # 'image': open(fpath, 'rb'),
                },
                data=data
            )
            resp = r.text
            print(resp)

            if "videoURL" in resp:
                os.remove(json_path)
                os.remove(fpath)
                os.remove(encoded_fpath)

        except requests.exceptions.ConnectionError:  # no internet connection
            print("batch not sent")
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            print(e)

    def send_loop(self):
        while self.work or (not self.work and self.queue.qsize() > 0):
            if self.COLLECTION_TOKEN is None:
                self.init_collection()
                continue
            if self.check_untreated_data():
                self.send_remaining_data()
            json_path = self.queue.get()
            try:
                self.send_request(json_path)
            except:
                continue

    def push_data(self, data):
        self.queue.put(data)


def create_token():

    try:
        r = requests.post(
            URL,
            headers={'Token': TRUCK_TOKEN},
            json={
                "startAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        )
        data = json.loads(r.text)
        return data['ID']
    except requests.exceptions.ConnectionError:  # no internet connection
        print("collection not created")
        return None


def get_token(path):
    path = path+'/connection_token.txt'
    if is_old_collect(path):
        f = open(path, 'r')
        token = f.read()
        return token
    else:
        token = create_token()
        if token is None:
            return None
        f = open(path, 'w')
        f.write(token)
        f.close()
        return token


def is_old_collect(path='connection_token.txt'):
    if os.path.exists(path):
        mtime = os.path.getmtime(path)
        file_date = datetime.fromtimestamp(mtime)
        file_date = file_date.date()
        today_date = '20'+datetime.now().strftime('%y-%m-%d')
        return today_date == str(file_date)
    return False


if __name__ == '__main__':
    off = office('./data/')
    sleep(10)
    off.work = False
