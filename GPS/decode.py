import base64
import cv2
import numpy as np
from PIL import Image


#example of data is encoded on the jetson side
frame = cv2.imread('gd.jpg')
var = base64.b64encode(cv2.imencode('.png', frame)[1]).decode()


#var is now a string
#how to decode the data after it becomes a string in json
var = base64.b64decode(var)
var = np.fromstring(var, dtype='uint8')
im=cv2.imdecode(var, cv2.IMREAD_UNCHANGED)

cv2.imshow('',im)
cv2.waitKey(0)
