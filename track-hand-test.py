import cv2
import numpy as np
cap = cv2.VideoCapture(0)

#import ipdb; ipdb.set_trace()
x,y=0,0

while( cap.isOpened() ) :
    ret,img = cap.read()

    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(5,5),0)
    ret,thresh1 = cv2.threshold(blur,70,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

    contours, hierarchy = cv2.findContours(thresh1,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    drawing = np.zeros(img.shape,np.uint8)

    max_area = 0
    ci = 0
    for i in range(len(contours)):
            cnt = contours[i]
            area = cv2.contourArea(cnt)
            if(area > max_area):
                max_area = area
                ci = i

    cnt = contours[ci]
    hull = cv2.convexHull(cnt)
    """
    moments = cv2.moments(cnt)
    if moments['m00']!=0:
                cx = int(moments['m10']/moments['m00']) # cx = M10/M00
                cy = int(moments['m01']/moments['m00']) # cy = M01/M00
    centr=(cx,cy)       
    cv2.circle(img,centr,5,[0,0,255],2)       
    """

    cv2.drawContours(drawing,[cnt],0,(0,255,0),2)

    #cnt = cv2.approxPolyDP(cnt,0.01*cv2.arcLength(cnt,True),True)
    hand = np.array(sorted(cnt, key=lambda x:x[0][0], reverse=True)[0:len(cnt)*15/100])
    cv2.drawContours(drawing,[hand],0,(0,0,255),2) 

    # test moving circle
    cv2.circle(drawing, (x,y), 10, (120,120,0))
    x+=1
    y+=1


    #cv2.drawContours(drawing,[hull],0,(0,0,255),2) 
    
    #hull = cv2.convexHull(cnt,returnPoints = False)

    cv2.imshow('output',drawing)
    cv2.imshow('input',gray)
    
                
    k = cv2.waitKey(10)
    if k == 27:
        break