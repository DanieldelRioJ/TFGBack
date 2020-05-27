import numpy as np
import math
import cv2
from helpers import Helper
from utils.Constants import PERSON_WIDTH
import matplotlib.pyplot as plt

def __calculate_speed__(object_map,one_meter,fps):
    for id,obj in object_map.items():
        apA=obj.appearances[0]
        mean=0
        for appearance in obj.appearances[1:]:
            #Calculate real distance in m/s
            distance=Helper.distance(*apA.real_coordinates,*appearance.real_coordinates)
            speed=fps*distance/one_meter
            mean+=speed
            appearance.speed=speed
            apA=appearance
        obj.average_speed=mean/(len(obj.appearances)-1)

def order_points_right(pts):
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
    return ordered_array,distances.min(),min_arg

def order_points_left(pts):
    max_dimensions=pts.max(axis=0)
    distances=np.zeros(4)
    limits=np.array([[0,0],[max_dimensions[0],0],max_dimensions,[0,max_dimensions[1]]])
    for i in range(4):
        for j in range(4):
            pos_distance_array=(-i-j)%4
            distance=Helper.distance(*pts[i],*limits[pos_distance_array])
            distances[j]+=distance
    min_arg=distances.argmin()

    ordered_array=np.zeros((4,2),dtype="float32")
    for i in range(0,4):
        new_position=(-i-min_arg)%4
        ordered_array[new_position]=pts[i]
    return ordered_array,distances.min(),min_arg


def getRealWorldPoint(M, point):
    point = np.array([point[0], point[1], 1]).reshape(3, 1)
    point = np.matmul(M, point)
    return np.array([point[0] / point[2], point[1] / point[2]])


def add_real_coordinates(points, object_map,references,ratio,fps):
    points = np.array(points, dtype="float32")
    (tl, tr, br, bl) = points

    #Select better order,clockwise or counter clockwise
    points_ordered_left,left_distances, first_point_left = order_points_left(points)
    points_ordered_right,right_distances,first_point_right=order_points_right(points)

    if right_distances<left_distances:
        points=points_ordered_right
        if ratio is not None:
            #try to gess if the ratio is for width of height and calculate it
            if first_point_right==0 or first_point_right==2: #width
                ratio=1/ratio

    else:
        points=points_ordered_left
        if ratio is not None:
            if first_point_left==1 or first_point_left==3: #width
                ratio=1/ratio

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
    if ratio is None:

        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))
    else:
        maxHeight = maxWidth * ratio
    # now that we have the dimensions of the new image, construct
    # the set of destination points to obtain a "birds eye view",
    # (i.e. top-down view) of the image, again specifying points
    # in the top-left, top-right, bottom-right, and bottom-left
    # order
    #maxHeight=int(maxWidth*0.7)
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")
    # compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(points, dst)

    # TEST
    """img = cv2.imread("background.jpg")
    warped = cv2.warpPerspective(img, M, (maxWidth,maxHeight))

    cv2.namedWindow('img', cv2.WINDOW_NORMAL)
    cv2.imshow("img", warped)
    cv2.waitKey()
    cv2.destroyWindow("img")"""

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

    #Estimate conversion between points and meters
    shoudler_width_values=[]
    for id,obj in object_map.items():
        for appearance in obj.appearances[::50]:
            real_w_point_a=getRealWorldPoint(M,(appearance.col,appearance.row+appearance.h))
            real_w_point_b = getRealWorldPoint(M, (appearance.col+appearance.w, appearance.row + appearance.h))
            shoudler_width_values.append(Helper.distance(*real_w_point_a,*real_w_point_b))
    mean=np.mean(shoudler_width_values)
    one_meter=100*mean/PERSON_WIDTH

    __calculate_speed__(object_map, one_meter,fps)

    #Calculate reference points
    converted_references = []
    if references is not None:
        for array in references:
            new_array=[]
            for point in array:
                new_point=getRealWorldPoint(M, (point['x'],point['y'])).tolist()
                new_array.append({'x':new_point[0][0],'y':new_point[1][0]})
            converted_references.append(new_array)

    return object_map, [min_x,min_y], [max_x,max_y],int(one_meter),converted_references
