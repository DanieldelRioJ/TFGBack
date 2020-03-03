import cv2
import os
from functools import partial
from multiprocessing.dummy import Pool as ThreadPool

def read_image(path,i):
    fileName = str.format("{:06d}.jpg", i)
    img = cv2.imread(path + "img1/" + fileName)
    return img

def read_images(path): #format of images: 000000.jpg
    pool = ThreadPool(os.cpu_count())
    func=partial(read_image,path)
    results = pool.map(func, range(1, 796))
    pool.close()
    pool.join()
    return results

def get_frames_from_video(path):
    cap=cv2.VideoCapture(path)
    frames=[]
    i=1
    while(True):
        ok,frame=cap.read()
        if not ok or i>500:
            break
        print(i)
        frames.append(frame)
        i+=1
    cap.release()
    return frames