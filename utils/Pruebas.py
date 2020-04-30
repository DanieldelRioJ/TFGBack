import cv2
import numpy as np
from matplotlib import pyplot as plt
import math

import time

def getRealWorldPoint(M,point):
    point=np.array([point[0],point[1],1]).reshape(3,1)
    point=np.matmul(M,point)
    return np.array([point[0]/point[2],point[1]/point[2]])

def bounding_box(points):
    x_coordinates, y_coordinates = zip(*points)

    return [(min(x_coordinates), min(y_coordinates)), (max(x_coordinates), max(y_coordinates))]

def prueba():
    pts1 = []
    circles=[]

    img = cv2.imread('img2.jpeg')
    originalImage=img.copy()

    def funcCallBack(event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN:
            print("new click")
            pts1.append((x, y))
        elif event==cv2.EVENT_RBUTTONDOWN:
            print("right")
            circles.append((x, y))

    cv2.namedWindow('img', cv2.WINDOW_KEEPRATIO)
    cv2.setMouseCallback("img", funcCallBack)
    cv2.resizeWindow('img', 600, 400)
    cv2.imshow("img", img)
    cv2.waitKey()

    for circle in circles:
        img=cv2.circle(img,(circle[0],circle[1]),15,(255,0,0),-1)

    pts1=np.array(pts1,dtype = "float32")

    ratio = 1.6
    cardH = int(math.sqrt(
        (pts1[2][0] - pts1[1][0]) * (pts1[2][0] - pts1[1][0]) + (pts1[2][1] - pts1[1][1]) * (pts1[2][1] - pts1[1][1])))
    cardW =int( ratio * cardH);
    """pts2 = np.float32(
        [[pts1[0][0], pts1[0][1]], [pts1[0][0] + cardW, pts1[0][1]], [pts1[0][0] + cardW, pts1[0][1] + cardH],
         [pts1[0][0], pts1[0][1] + cardH]])"""
    pts2=np.array([
		[0, 0],
		[cardW - 1, 0],
		[cardW - 1, cardH - 1],
		[0, cardH - 1]], dtype = "float32")

    M = cv2.getPerspectiveTransform(pts1, pts2)

    ptIS=getRealWorldPoint(M,[0,0])

    deformated=originalImage.copy()
    dst = cv2.warpPerspective(deformated, M, (cardW, cardH))

    for circle in circles:
        rw=getRealWorldPoint(M,circle)
        dst=cv2.circle(dst,(rw[0],rw[1]),15,(255,0,0),-1)


    plt.subplot(121), plt.imshow(img), plt.title('Input')
    plt.subplot(122), plt.imshow(dst), plt.title('Output')
    plt.show()



"""
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
"""
"""
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
    """