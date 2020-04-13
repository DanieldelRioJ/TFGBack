from sklearn.linear_model import LinearRegression
from helpers import Helper
from utils import ConfigValues
import numpy as np
import math
import cv2

#Get direction angle expresed in radians
def get_direction_angle(points):
    points=__reduce_point_number__(points)
    X=np.array([point.x for point in points]).reshape(-1,1)
    Y=np.array([point.y for point in points])
    regressor=LinearRegression().fit(X,Y)
    r2=regressor.score(X,Y)
    if r2 < ConfigValues.ERRATIC_MOVEMENT_MINIMUM_R2:
        return None
    return math.atan(regressor.coef_[0])

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