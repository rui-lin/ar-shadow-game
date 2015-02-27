# faceMinx - right hand side, points to minx
# person is mirror on screen ()
#
# Change hand % based on in or outside screen

import cv2
import numpy as np
from scipy import stats
import math
import random


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
        self.calibration_inprogress = False
        self.calibration_bgsubtractor = cv2.BackgroundSubtractorMOG(backgroundRatio=0.5, nmixtures=2, history=10) #0.3,30
        self.calibration_counter = 0

    history = 50
    fgbg = cv2.BackgroundSubtractorMOG(backgroundRatio=0.3, nmixtures=30, history=history) #0.3,30
    learn_counter = history
    count = 0
    MAXX = 1280
    MAXY = 720

    # Need native call to get otherwise
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 1024

    MARGIN_BOTTOM = 50
    MARGIN_TOP = 150
    MARGIN_LEFT = 300
    MARGIN_RIGHT = 300

    EFFECTIVE_CAM_WIDTH = MAXX - MARGIN_LEFT - MARGIN_RIGHT
    EFFECTIVE_CAM_HEIGHT = MAXY - MARGIN_TOP - MARGIN_BOTTOM

    def circle_touch(self, ax, ay, ar, bx, by, br):
        return (ax-bx)**2 + (ay-by)**2 <= (ar+br)**2

    def filter_only_center(self, arr):
        return np.array([x for x in arr if self.circle_touch(x[0][0], x[0][1], 0, self.MAXX/2, self.MAXY/2, 300)])

    def calibrate_background(self):
        self.learn_counter = self.history

    def cropImageToScreen(self, img):
        trans = img[self.MARGIN_BOTTOM:-self.MARGIN_TOP] # y's
        trans = np.array([x[self.MARGIN_LEFT:-self.MARGIN_RIGHT] for x in trans]) #x's
        #trans = cv2.resize(trans, dsize=(self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        return trans

    def scaleContoursToDisplay(self, contours):
        for x in contours:
            x[0][0] = x[0][0]*self.SCREEN_WIDTH/self.EFFECTIVE_CAM_WIDTH
            x[0][1] = x[0][1]*self.SCREEN_HEIGHT/self.EFFECTIVE_CAM_HEIGHT

    def update(self, img, drawing):
        screen_img = self.cropImageToScreen(img)

        #gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        #blur = cv2.GaussianBlur(gray,(5,5),0)

        masked_img = 0
        if self.learn_counter:
            print "learning"
            masked_img = self.fgbg.apply(screen_img, learningRate = 1.0/self.history)
            self.learn_counter -= 1
        else:
            masked_img = self.fgbg.apply(screen_img, learningRate = 0)

        #ret, thresh1 = cv2.threshold(masked_img,70,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        

        cv2.imshow('img', screen_img)
        cv2.imshow('masked',masked_img)

        contours, hierarchy = cv2.findContours(masked_img,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

        max_area = 0
        ci = 0
        for i in range(len(contours)):
                cnt = contours[i]
                area = cv2.contourArea(cnt)
                if(area > max_area):
                    max_area = area
                    ci = i

        cnt = contours[ci]
        self.scaleContoursToDisplay(cnt)

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

    def isCalibrationDone(self):
        return not self.calibration_inprogress

    def startCalibration(self):
        self.calibration_bgsubtractor = cv2.BackgroundSubtractorMOG(backgroundRatio=0.5, nmixtures=2, history=20) #0.3,30
        self.calibration_counter = 20
        self.calibration_inprogress = True

    def calibrationStep(self, img, drawing):
        if not self.calibration_counter:
            self.calibration_inprogress = False
            return

        masked_img = self.calibration_bgsubtractor.apply(img, learningRate = 0.1/10)
        self.calibration_counter -= 1
        
        contours, hierarchy = cv2.findContours(masked_img,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return

        cnt = self.getLargestContour(contours)
        boundingRect = cv2.boundingRect(cnt) # use this
        
        print boundingRect
        cv2.rectangle(drawing, (boundingRect[0], boundingRect[1]), (boundingRect[2], boundingRect[3]), (0,255,255), 10)

    def renderCalibrationDisplay(self, drawing):
        rgb = (
            ((self.calibration_counter * 133) % 256),
            ((self.calibration_counter * 133) % 256),
            ((self.calibration_counter * 133) % 256))
        cv2.rectangle(drawing, (0,0), (SCREEN_WIDTH, SCREEN_HEIGHT), rgb, -1)

    def getLargestContour(self, contours):
        max_area = 0
        ci = 0
        for i in range(len(contours)):
            cnt = contours[i]
            area = cv2.contourArea(cnt)
            if(area > max_area):
                max_area = area
                ci = i

        return contours[ci]





