import cv2
import numpy as np

from time import time
from threading import Thread

def sharpness(frame):
	return cv2.Laplacian(frame, cv2.CV_64F).var()
class local_sim(object):
	"""docstring for local_sim"""
	def __init__(self):
		super(local_sim, self).__init__()
		self.first = True
		self.maps = None
	def similair(self, i, j):
		img = self.frame[i-1 : i+2, j-1:j+2]
		s = img.reshape(-1)
		return np.array([(abs(j - s[1]) < 10) for j in s]).all() == True

	def clear_patches(self, img):
		h,w = img.shape	
		return [[self.similair(i,j) for j in range(1,w - 2)] for i in range( 1, h-2 )]

	def compactness(self, frame):
		frame = cv2.resize(frame, (32, 64))
		frame = frame[0:10, ...]
		gray = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
		self.frame = gray[:,:,0]
		if self.maps is None :
			self.maps = np.zeros(self.frame.shape)
		im1 = np.array(self.clear_patches_bin())
		#return np.count_nonzero(im1[20:,:,0]), np.count_nonzero(im1[:8,:,1]) 
		return  np.count_nonzero(self.maps[:8,:])

	def create_threads(self, h,w, ):
		self.maps = np.zeros((h,w))
		self.threads = np.array([[Thread(target = self.similair_bin, args=(i,j))  for j in range(1,w - 2)] for i in range( 1, h-2 )]).reshape(-1)
		for t in self.threads :
			t.start()

	def clear_patches_bin(self):
		h,w = self.frame.shape

		#self.maps = np.array([[(abs(self.frame[i-1 : i+2, j-1:j+2] - self.frame[i,j]) < 5).all() for i in range(1, h-2)] for j in range (1, w-2)])
		#return 
		for j in range(1,w - 2):
			for i in range( 1, h-2 ):
				img = abs(self.frame[i-1 : i+2, j-1:j+2] - self.frame[i,j])
				#return (np.array([(abs(j - s[4]) < 10) for j in s]).all() == True, np.array([(abs(j - t[4]) < 2) for j in t]).all() == True)
				self.maps[i,j] =  (img<5).all()


	def similair_bin(self, i,j):
		#s = img[...,1].reshape(-1)
		img = self.frame[i-1 : i+2, j-1:j+2]
		t = img.reshape(-1)
		#return (np.array([(abs(j - s[4]) < 10) for j in s]).all() == True, np.array([(abs(j - t[4]) < 2) for j in t]).all() == True)
		self.maps[i,j] =  np.array([(abs(j - t[4]) < 5) for j in t]).all() 

	def bin_exist(self, frame):

		frame = cv2.resize(frame, (32,32))
		self.frame = frame
		hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
		im = clear_patches_bin(hsv[:,:,0:2])
		return cv2.countNonZero(im[:8,:]) 


"""
cap = cv2.VideoCapture('3.h264')
cap.set(1,17100)

while(cap.isOpened()):
    # Capture frame-by-frame
    ret, frame = cap.read()	
    t = frame.copy()
    frame = cv2.resize(frame, (32,32))
    gray = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    im = np.array(clear_patches(gray[:,:,1]), np.uint8)
    summ = np.sum(im[20:, ...], axis = 1)
    if np.max(summ) >  4  :
    	print(np.argmax(summ) + 24, summ)


    im = cv2.resize(im, (512,512))
    t = cv2.resize(t, (512,512))

    cv2.imshow('',im * 255)
    cv2.imshow('orig',t)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
"""
