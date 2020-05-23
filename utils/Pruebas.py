import cv2
import numpy as np
from matplotlib import pyplot as plt
from helpers import PerspectiveHelper
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

    pts=np.array([[166,161],[334,176],[249,213],[60,193]],dtype=int)
    print(pts)
    pts = np.array([[60, 193],[166, 161], [334, 176], [249, 213]], dtype=int)
    pts=PerspectiveHelper.order_points(pts)
    print(pts)

    """
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
    plt.show()"""

def pruebaHistogram():
    img = cv2.imread('186.jpg')
    img=img[0:img.shape[0]//2]
    #img=img[img.shape[0]//2:]
    cv2.imshow('original', img)


    Z = img.reshape((-1, 3))

    # convert to np.float32
    Z = np.float32(Z)

    start = time.time()

    # define criteria, number of clusters(K) and apply kmeans()
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    K = 3
    ret, label, center = cv2.kmeans(Z, K, None, criteria, 2, cv2.KMEANS_RANDOM_CENTERS)

    end = time.time()
    print(end - start)


    # Now convert back into uint8, and make original image
    center = np.uint8(center)
    res = center[label.flatten()]
    res2 = res.reshape((img.shape))

    cv2.imshow('res2', res2)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def pruebaHistogramv1():
    img1=cv2.imread("./img1.jpeg")
    img1=img1//32
    cv2.imshow("img",img1)
    cv2.waitKey()
    cv2.imshow("img", img1*32)
    cv2.waitKey()
    g,b,r=cv2.split(img1)
    result=g+b*8+r*64
    hist=cv2.calcHist([result],[0],None,[512],[0,510])
    plt.plot(hist)
    plt.show()

    max_value=np.argmax(hist)
    r=max_value//64
    max_value%=64
    b=max_value//8
    g=max_value%8
    color=(g*32,b*32,r*32)
    img=np.full((255,255,3),color,dtype=np.uint8)
    cv2.imshow("img",img)
    cv2.waitKey()
    print(color)

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