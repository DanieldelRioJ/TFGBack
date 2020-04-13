import cv2
from matplotlib import pyplot as plt

def prueba():
    img=cv2.imread("./image.png")
    hist=cv2.calcHist([img,img,img],[0],None,[256],[0,256])
    plt.plot(hist)
    plt.xlim([0, 256])


    plt.show()
    print(hist)