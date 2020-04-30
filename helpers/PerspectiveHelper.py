import numpy as np
import cv2
import matplotlib.pyplot as plt

def order_points(pts):
    # initialzie a list of coordinates that will be ordered
    # such that the first entry in the list is the top-left,
    # the second entry is the top-right, the third is the
    # bottom-right, and the fourth is the bottom-left
    rect = np.zeros((4, 2), dtype="float32")
    # the top-left point will have the smallest sum, whereas
    # the bottom-right point will have the largest sum
    s = pts.sum(axis=1)

    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    # now, compute the difference between the points, the
    # top-right point will have the smallest difference,
    # whereas the bottom-left will have the largest difference
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    # return the ordered coordinates
    return rect

def getRealWorldPoint(M,point):
    point=np.array([point[0],point[1],1]).reshape(3,1)
    point=np.matmul(M,point)
    return np.array([point[0]/point[2],point[1]/point[2]])

def add_real_coordinates(points, object_map):
    points=np.array(points,dtype="float32")
    (tl, tr, br, bl) = points

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

    real_coordinates_array=[]
    for obj_id in object_map:
        obj=object_map.get(obj_id)
        for appearance in obj.appearances:
            real_coordinates=getRealWorldPoint(M,(appearance.center_col,appearance.center_row))
            real_coordinates_array.append(real_coordinates)
            appearance.real_coordinates=(int(real_coordinates[0]),int(real_coordinates[1]))

    #TEST
    #img=cv2.imread("background.jpg")
    #warped=cv2.warpPerspective(img,M,img.shape[:-1])

    real_coordinates_array=np.array(real_coordinates_array)
    upper_left_limit=real_coordinates_array.min(axis=0)
    lower_right_limit=real_coordinates_array.max(axis=0)
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
    return object_map,upper_left_limit.tolist(),lower_right_limit.tolist()