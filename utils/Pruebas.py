import cv2
import numpy as np
from matplotlib import pyplot as plt

import time

def function(row):
    row=row.reshape(1,len(row))
    hist = cv2.calcHist(row, [0], None, [16], [0, 16])
    max_color=np.argmax(hist) #Index of the most repeated value
    max_quantity=max(hist)[0] #Most repeated quantity
    hist[max_color]=-1
    second_max_quantity=max(hist)[0] #Second Most repeated quantity
    if second_max_quantity*2<max_quantity: #If the difference is big, consider it, else, return -1
        return np.uint8(max_color)
    return np.uint8(255)

def prueba():
    start = time.time()

    images = [cv2.imread("./image1.png"), cv2.imread("./image2.png"),cv2.imread("./image3.png"),cv2.imread("./image4.png")]
    original_shape = images[0].shape[:-1]

    #Reduce size for optimization purposes
    images = [cv2.pyrDown(img) for img in images]
    images = np.array(images) // 16 #Reduce color from 255 to 16 poxible values per color (reduce quality, but also noise).


    new_array = np.apply_along_axis(function, 0, images)

    end = time.time()
    print(end - start)

    channels=cv2.split(new_array)

    masks=[cv2.threshold(channel,254,255,cv2.THRESH_BINARY_INV) for channel in channels] #Create mask for eaach channel. It mask invalid values

    mask=cv2.bitwise_and(masks[0][1],masks[1][1]) #second element of the mask, remember, threshold return 2 values, second is the mask
    mask=cv2.bitwise_and(mask,masks[2][1])

    new_array=cv2.bitwise_and(new_array,new_array,mask=mask)

    pyredUp=cv2.pyrUp(new_array*16)

    result=cv2.resize(pyredUp,(original_shape[1],original_shape[0]))
    mask=cv2.resize(mask,(original_shape[1],original_shape[0]))

    return result,mask