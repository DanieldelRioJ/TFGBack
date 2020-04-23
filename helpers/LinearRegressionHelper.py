from sklearn.linear_model import LinearRegression
from helpers import Helper
from utils import ConfigValues
from shapely.ops import nearest_points
from shapely.geometry import LineString,Point
import numpy as np
import math
import cv2

#Get direction angle expresed in radians
def get_direction_angle(points):
    points=__reduce_point_number__(points)
    furthest_point_index=__index_of_furthest_point__(points)

    #If the movements go straight and back, we consider it erratic movement
    if furthest_point_index/len(points)<ConfigValues.PORCENTAGE_PERMITTED_FURTHEST_POINT:
        return None,None
    X=np.array([point.x for point in points]).reshape(-1,1)
    Y=np.array([point.y for point in points])
    regressor=LinearRegression().fit(X,Y)
    r2=regressor.score(X,Y)

    #If the direction is erratic
    if r2 < ConfigValues.ERRATIC_MOVEMENT_MINIMUM_R2:
        return None,None

    #Now calculate the real angle
    x_coef=regressor.coef_[0]

    #calculate point at x=-10000 and x=10000
    first_y=-10000*x_coef
    last_y=10000*x_coef

    line=LineString([(-10000,first_y),(10000,last_y)])
    first_point_outline=Point(points[0].x,points[0].y)
    last_point_outline = Point(points[-1].x, points[-1].y)

    first_point_inline=nearest_points(line,first_point_outline)[0].bounds
    last_point_inline = nearest_points(line, last_point_outline)[0].bounds

    x=last_point_inline[0]-first_point_inline[0]
    y = last_point_inline[1] - first_point_inline[1]

    angle=math.atan2(y,x)
    if angle<0:
        angle=angle+math.pi*2
    return angle,Helper.distance(0,0,x,y)

#Returst the index of the furthest point in the list compared with the first point
def __index_of_furthest_point__(points):
    start_point=points[0]
    furthest_point_index=0
    furthest_distance=0
    for i,point in enumerate(points[1:]):
        distance=Helper.distance(start_point.x,start_point.y,point.x,point.y)
        if distance>furthest_distance:
            furthest_point_index=i
            furthest_distance=distance
    return furthest_point_index

#delete some points that are closed to reduce time calculation
def __reduce_point_number__(points,range=10):
    aux_points=[]
    last_point=points[0]
    aux_points.append(last_point)

    for point in points:
        if Helper.distance(last_point.x,last_point.y,point.x,point.y) > range:
            aux_points.append(point)
            last_point=point

    return aux_points