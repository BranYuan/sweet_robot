# -*- coding: utf-8 -*-
"""
Created on Sat Mar  2 15:02:36 2019

opencv
numpy
pandas


@author: asmaa
"""

import cv2
import numpy as np
import pandas as pd
import time


# s越大 读到的干扰量越多
def process_frame(frame, s = 15):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    sensitivity = s
    lower_white = np.array([0,0,255-sensitivity], dtype=np.uint8)
    upper_white = np.array([255,sensitivity,255], dtype=np.uint8)
    
    mask = cv2.inRange(hsv, lower_white, upper_white)
    result = cv2.bitwise_and(frame, frame, mask= mask)
    
    gray = cv2.cvtColor(result, cv2.COLOR_RGB2GRAY)
    binary_output = np.zeros_like(gray)
    binary_output[gray != 0] = 1
    
    height, width = gray.shape
    xy = pd.DataFrame(np.dstack((gray.nonzero()[0],gray.nonzero()[1]))[0],columns=['y','x'])
    
    upper_percentage = xy[xy['y'] > height/2]['x'].mean()/width
    lower_percentage = xy[xy['y'] < height/2]['x'].mean()/width
    #print(xy[xy['y'] > height/2]['x'].mean()/width)
    #print(xy[xy['y'] < height/2]['x'].mean()/width)
    
    #result = cv2.putText(result, xy[xy['y'] > height/2]['x'].mean()/width, (2,2), 0, 1, (0,0,0), 2, cv2.LINE_AA)
    #result = cv2.putText(result, xy[xy['y'] < height/2]['x'].mean()/width, (2,4), 0, 1, (0,0,0), 2, cv2.LINE_AA)
    
    return result, upper_percentage, lower_percentage


def main():
    cv2.namedWindow("preview")
    
    #参数调节摄像头，如果只有一个摄像头 则为0
    vc = cv2.VideoCapture(0)

    if vc.isOpened():
        rval, frame = vc.read()
    else:
        rval = False
        
    while rval:
        cv2.imshow("preview", frame)
        rval, frame = vc.read()
        
        frame,upper_percentage, lower_percentage = process_frame(frame,30)
        print([upper_percentage,lower_percentage])
        key = cv2.waitKey(20)
        if key == 27:
            break


        time.sleep(0.1)
        
    cv2.destroyWindow("preview")
    vc.release()


if __name__ == "__main__":
    main()



















