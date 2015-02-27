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

    history = 50
    fgbg = cv2.BackgroundSubtractorMOG(backgroundRatio=0.5, nmixtures=10, history=history)
    learn_counter = history
    count = 0
    MAXX = 1280
    MAXY = 720

    def circle_touch(self, ax, ay, ar, bx, by, br):
        return (ax-bx)**2 + (ay-by)**2 <= (ar+br)**2

    def filter_only_center(self, arr):
        return np.array([x for x in arr if self.circle_touch(x[0][0], x[0][1], 0, self.MAXX/2, self.MAXY/2, 300)])

    def update(self, img, drawing):
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray,(5,5),0)

        masked_img = 0
        if self.learn_counter:
            masked_img = self.fgbg.apply(gray, learningRate = 1.0/self.history)
            self.learn_counter -= 1
        else:
            masked_img = self.fgbg.apply(gray, learningRate = 0)

        #ret, thresh1 = cv2.threshold(masked_img,70,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        #import ipdb; ipdb.set_trace()

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
        
        hull = cv2.convexHull(cnt, returnPoints = False)
        defects = cv2.convexityDefects(cnt, hull)

        if defects is not None and len(defects) > 0:
            sorted_defects = sorted(defects, key=lambda x:x[0][3], reverse=True)
            farthest_point = cnt[sorted_defects[0][0][2]]
        else:
            farthest_point = [[0, 0]]

        """
        moments = cv2.moments(cnt)
        if moments['m00']!=0:
                    cx = int(moments['m10']/moments['m00']) # cx = M10/M00
                    cy = int(moments['m01']/moments['m00']) # cy = M01/M00
        centr=(cx,cy)       
        cv2.circle(img,centr,5,[0,0,255],2)       
        """

        (x, y), rad = cv2.minEnclosingCircle(cnt)

        if self.count >= 0:
            if farthest_point[0][0] < x:
                rev = True
            else:
                rev = False

            self.count += 1

        #cv2.drawContours(drawing,[cnt],0,(0,255,0),2)

        #cnt = cv2.approxPolyDP(cnt,0.01*cv2.arcLength(cnt,True),True)
        #cnt = self.filter_only_center(cnt)
        hand = np.array(sorted(cnt, key=lambda x:x[0][0], reverse=rev)[0:len(cnt)*50/100])

        x = [p[0][0] for p in hand]
        y = [p[0][1] for p in hand]
        slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)

        #print (int(np.mean(x)), int(np.mean(y)))
        cv2.circle(drawing, (int(np.mean(x)),int(np.mean(y))), 70, (255,0,0), -1)
 
        self.cnt = cnt
        self.hand = hand
        self.slope = slope
        self.intercept = intercept
        #cv2.drawContours(drawing,[hull],0,(0,0,255),2) 

    def render(self, drawing):
        try:
            cv2.drawContours(drawing,[self.cnt],0,(0,255,0),2) 
            cv2.drawContours(drawing,[self.hand],0,(0,255,255),2)
            print (0, self.intercept), (1000, 1000*self.slope)
            if not math.isnan(self.slope):
                cv2.line(drawing, (0, int(self.intercept)), (1000, int(1000*self.slope+self.intercept)), (0,0,255),10)
        except Exception as e:
            pass

