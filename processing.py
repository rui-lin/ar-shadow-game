# faceMinx - right hand side, points to minx
# person is mirror on screen ()
#
# Change hand % based on in or outside screen

import cv2
import numpy as np
from scipy import stats
import math

class ImageProcessor:
    def __init__(self):
        self.cnt = []
        self.hand = []
        self.slope = 0
        self.intercept = 0
        self.faceMinx = True
        self.handcx = 0
        self.handcy = 0
        self.angle = 0

    history = 50
    fgbg = cv2.BackgroundSubtractorMOG(backgroundRatio=0.3, nmixtures=50, history=history)
    learn_counter = history
    count = 0
    MAXX = 1280
    MAXY = 720

    def circle_touch(self, ax, ay, ar, bx, by, br):
        return (ax-bx)**2 + (ay-by)**2 <= (ar+br)**2

    def filter_only_center(self, arr):
        return np.array([x for x in arr if self.circle_touch(x[0][0], x[0][1], 0, self.MAXX/2, self.MAXY/2, 300)])

    def calibrate_background(self):
        self.learn_counter = self.history

    def update(self, img, drawing):
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray,(5,5),0)

        masked_img = 0
        if self.learn_counter:
            masked_img = self.fgbg.apply(img, learningRate = 1.0/self.history)
            self.learn_counter -= 1
        else:
            masked_img = self.fgbg.apply(img, learningRate = 0)

        #ret, thresh1 = cv2.threshold(masked_img,70,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        #import ipdb; ipdb.set_trace()

        cv2.imshow('img', img)
        cv2.imshow('masked',masked_img)

        contours, hierarchy = cv2.findContours(masked_img,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return

        max_area = 0
        ci = 0
        for i in range(len(contours)):
                cnt = contours[i]
                area = cv2.contourArea(cnt)
                if(area > max_area):
                    max_area = area
                    ci = i

        cnt = contours[ci]

        meanx = np.mean([x[0][0] for x in cnt])
        faceMinx = True
        if meanx < self.MAXX/2.0:
            faceMinx = True
        else:
            faceMinx = False
        
        hand = np.array(sorted(cnt, key=lambda x:x[0][0], reverse=faceMinx)[0:len(cnt)*80/100]) # or 20 for body - todo update
        hand_hull = cv2.convexHull(hand)

        x = [p[0][0] for p in hand_hull]
        y = [p[0][1] for p in hand_hull]
        slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)

        handcx = int(np.mean(x))
        handcy = int(np.mean(y))

        cv2.circle(drawing, (handcx, handcy), 70, (255,0,0), -1)
 
        self.cnt = cnt
        self.cnt_hull = cv2.convexHull(cnt)
        self.hand = hand
        self.slope = slope
        self.intercept = intercept
        self.handcx = handcx
        self.handcy = handcy
        self.faceMinx = faceMinx
        self.angle = math.atan2(slope * -1 if faceMinx else slope * 1, 1 if faceMinx else -1) # y,x

    def renderDebug(self, drawing):
        cv2.drawContours(drawing,[self.cnt],0,(0,255,0),2) 
        cv2.drawContours(drawing,[self.hand],0,(0,255,255),2)
        #print (0, self.intercept), (1000, 1000*self.slope)

        if not math.isnan(self.slope):
            cv2.line(drawing, (0, int(self.intercept)), (1000, int(1000*self.slope+self.intercept)), (0,0,255),10)

    def renderDisplay(self, drawing):
        # draw contour
        cv2.drawContours(drawing, [self.cnt_hull],0,(0,255,0),2)


