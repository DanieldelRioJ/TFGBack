import numpy as np
import math
import cv2
from helpers import Helper
from utils.Constants import PERSON_WIDTH
import matplotlib.pyplot as plt

def order_points(pts):
    max_dimensions=pts.max(axis=0)
    distances=np.zeros(4)
    limits=np.array([[0,0],[max_dimensions[0],0],max_dimensions,[0,max_dimensions[1]]])
    for i in range(4):
        for j in range(4):
            pos_distance_array=(i+j)%4
            distance=Helper.distance(*pts[i],*limits[pos_distance_array])
            distances[j]+=distance
    min_arg=distances.argmin()

    ordered_array=np.zeros((4,2),dtype="float32")
    for i in range(0,4):
        new_position=(i+min_arg)%4
        ordered_array[new_position]=pts[i]
    return ordered_array


def getRealWorldPoint(M, point):
    point = np.array([point[0], point[1], 1]).reshape(3, 1)
    point = np.matmul(M, point)
    return np.array([point[0] / point[2], point[1] / point[2]])


def add_real_coordinates(points, object_map):
    points = np.array(points, dtype="float32")
    (tl, tr, br, bl) = points

    points = order_points(points)

    (tl, tr, br, bl)=points

    # compute the width of the new image, which will be the
    # maximum distance between bottom-right and bottom-left
    # x-coordiates or the top-right and top-left x-coordinates
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    # compute the height of the new image, which will be the
    # maximum distance between the top-right and bottom-right
    # y-coordinates or the top-left and bottom-left y-coordinates
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    # now that we have the dimensions of the new image, construct
    # the set of destination points to obtain a "birds eye view",
    # (i.e. top-down view) of the image, again specifying points
    # in the top-left, top-right, bottom-right, and bottom-left
    # order
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")
    # compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(points, dst)

    real_coordinates_array = []
    max_x=0
    max_y=0
    min_x=None
    min_y=None
    for obj_id in object_map:
        obj = object_map.get(obj_id)
        for appearance in obj.appearances:
            real_coordinates = getRealWorldPoint(M, (appearance.col+appearance.w//2, appearance.row+appearance.h))
            real_coordinates_array.append(real_coordinates)
            appearance.real_coordinates = (int(real_coordinates[0]), int(real_coordinates[1]))

            if max_x<appearance.real_coordinates[0]:
                max_x=appearance.real_coordinates[0]
            elif min_x is None or min_x>appearance.real_coordinates[0]:
                min_x=appearance.real_coordinates[0]

            if max_y< appearance.real_coordinates[1]:
                max_y=appearance.real_coordinates[1]
            elif min_y is None or min_y>appearance.real_coordinates[1]:
                min_y=appearance.real_coordinates[1]

    # TEST
    # img=cv2.imread("background.jpg")
    # warped=cv2.warpPerspective(img,M,img.shape[:-1])
    """
    offsetX=int(upper_left_limit[0][0])
    offsetY=int(upper_left_limit[0][0])

    diference=(abs(int(upper_left_limit[0][0]-lower_right_limit[0][0])),abs(int(upper_left_limit[1][0]-lower_right_limit[1][0])))

    print(diference)
    img = np.zeros((diference[0], diference[1]))
    for appearance in object_map.get(9).appearances:
        cv2.circle(img,(appearance.real_coordinates[0]-offsetX,appearance.real_coordinates[1]-offsetY),5,(255,255,255),-1)

    cv2.namedWindow('img', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('img', 600, 600)
    cv2.imshow("img",img)
    cv2.waitKey()
    cv2.destroyWindow("img")
    """
    shoudler_width_values=[]
    for id,obj in object_map.items():
        for appearance in obj.appearances[::50]:
            real_w_point_a=getRealWorldPoint(M,(appearance.col,appearance.row+appearance.h))
            real_w_point_b = getRealWorldPoint(M, (appearance.col+appearance.w, appearance.row + appearance.h))
            shoudler_width_values.append(Helper.distance(*real_w_point_a,*real_w_point_b))
    mean=np.mean(shoudler_width_values)
    one_meter=100*mean/PERSON_WIDTH

    return object_map, [min_x,min_y], [max_x,max_y],int(one_meter)
