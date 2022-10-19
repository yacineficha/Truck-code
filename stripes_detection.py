import numpy as np
import cv2
import os


def get_center(i):
    M = cv2.moments(i)
    if M['m00'] != 0:
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])
        return [cx, cy]
    return [-1, -1]

def get_control_zones(center, max_step, offset = 0):
    return [((2 * center * s // max_step), (2 * center * (s+1) // max_step)) for s in range(offset, max_step - offset - 1) ]
    
def get_steps_required(sequence, center):
    m = np.mean(sequence)
    quarter = center // 2
    if m < quarter :
        return 0
    if m < center  :
        return 0
    if m < quarter + center:
        return 6
    
    return 2


    
def possible_stripe(sequence, center, center_y):
    steps = get_steps_required(sequence[..., 1], center_y)
    control_zones = get_control_zones(center=center, max_step=steps)
    misses = 0
    if steps == 0:
        n = np.count_nonzero(sequence[..., 0] > center)
        left, right = n, len(sequence) - n 
        #print(left, right, center, sequence)
        
        if (left > 2 and right > 2):
            return len(sequence) > 2
        return False
    if steps == 6:
        for b,e in control_zones:
            if np.count_nonzero(np.logical_and(e > sequence[..., 0], sequence[..., 0] > b)) == 0:
                misses+=1
        
        return misses < 4
    return len(sequence) > 3

def get_contours(img, color):
    
    kernel = np.ones((5, 5),np.uint8)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2Lab)
    lab = cv2.GaussianBlur(lab, (5, 5),
                       cv2.BORDER_DEFAULT)
                       
    lower = np.array([100,160,125])
    upper = np.array([190,195,145])

    
    mask1 = cv2.inRange(lab, lower, upper)

    #closing = cv2.morphologyEx(mask1, cv2.MORPH_OPEN, kernel)
    closing = cv2.morphologyEx(mask1  , cv2.MORPH_CLOSE, kernel)
    closing = cv2.dilate(closing, np.ones((7, 7),np.uint8))
    contours =cv2.findContours(closing,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)[0]

    #Loop through my contours to find rectangles and put them in a list, so i can view them individually later.
    cntrRect = []
    centers = []
    for i in contours:
            epsilon = 0.07*cv2.arcLength(i,True)
            approx = cv2.approxPolyDP(i,epsilon,True)
            if len(approx) == 4:
                
                cntrRect.append(i)
                centers.append(get_center(i))
    return cntrRect, centers

def get_colored_blocks(img, color):
    img_center_x, img_center_y = img.shape[1] // 2, img.shape[0] // 2
    cntrRect, centers = get_contours(img, color)
    
    img = cv2.drawContours(img,cntrRect,-1,(0,255,0),2)
    center_cnts = np.array(centers)
    if len(center_cnts) == 0:
        
        return -1
    center_cnts = np.array(sorted(center_cnts, key = lambda x : x[1]))
    centers = center_cnts[..., 1]
    
    centers_approximity = np.diff(centers)
    idx_centers = np.where(centers_approximity > 9)[0]
    length = len(idx_centers)
    if length == 0:
        possible_seq_idx = [(0, -1)]
    if length == 1:
        possible_seq_idx = [(0, idx_centers[0]), (idx_centers[0], -1)]
    else:
        idcs = []
        for i in range(length - 1):
            idx = idx_centers[i]
            idx_next = idx_centers[i+1]
            if idx_next - idx > 1:
                idcs.append((idx, idx_next))
        possible_seq_idx = idcs
        if len(possible_seq_idx) == 0:
            possible_seq_idx = [[0, -1]]    
        else:
            possible_seq_idx.append((idcs[-1][1], -1))
            possible_seq_idx.append((0, idcs[0][0]))

    contours_sequence = [center_cnts[x:y] for x,y in possible_seq_idx if y - x != 0] 
    box_sequence = [seq[..., 1].mean() for seq in contours_sequence if possible_stripe(seq, img_center_x, img_center_y)]
    if len(box_sequence) == 0:
        return -1
    
    
    return max(0, 256 - 20 - min(box_sequence))


def aruco_code_detection(Compactor_M, frame, curr_img, first_ok):
    img = cv2.resize(frame, (512, 256))
    rett = get_colored_blocks(img, 'red')
    return rett, True