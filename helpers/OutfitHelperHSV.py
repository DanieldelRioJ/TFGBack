from utils.Constants import PALETTE
import cv2
import numpy as np
from helpers import Helper
from io_tools.data import VideoInfDAO


# K means
def __obtain_colors__(img, K):
    Z = img.reshape((-1, 3))
    # convert to np.float32
    Z = np.float32(Z)

    # define criteria, number of clusters(K) and apply kmeans()
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    ret, label, center = cv2.kmeans(Z, K, None, criteria, 2, cv2.KMEANS_RANDOM_CENTERS)
    center = center.astype(np.uint8)

    """cv2.imshow("img",img)
    cv2.waitKey()"""

    for c in center:
        aux=np.uint8([[c]])
        (h, s, v)=cv2.cvtColor(aux, cv2.COLOR_BGR2HSV).tolist()[0][0]
        h *= 2
        s /= 2.5
        v /= 2.5
        c[0]=h
        c[1] = s
        c[2] = v

    center = [__obtain_palette_color__(c) for c in center]
    return center;


def __obtain_palette_color__(color):
    (h, s, v) = color
    if v < 15:  # black
        return 0
    elif v < 90 and s < 10:  # grey
        return 1
    elif s < 10 and v > 90:  # white
        return 2
    elif h >= 345 or h < 30:  # red
        return 3
    elif h >= 30 and h < 75:  # yellow
        return 4
    elif h >= 75 and h < 150:  # green
        return 5
    elif h >= 150 and h < 270:  # blue
        return 6
    else:  # pink h>=270 and h<345
        return 7

    return distances.argmin()


def __update_repetitions__(repetition_array, color_indexes):
    for i in color_indexes:
        repetition_array[i] += 1


def obtain_object_colors(video_obj, obj_dict):
    for id, obj in obj_dict.items():
        repetitions_up = np.zeros(len(PALETTE))
        repetitions_down = np.zeros(len(PALETTE))
        for appearance in obj.appearances[::10]:  # Use one picture each 50 (aprox 1 picture each 5 secs).
            sprite = VideoInfDAO.get_sprite(video_obj, id, appearance.frame)
            upper_part = sprite[0:sprite.shape[0] // 2]
            lower_part = sprite[sprite.shape[0] // 2:]

            upper_indexes = __obtain_colors__(upper_part, 2)
            lower_indexes = __obtain_colors__(lower_part, 2)

            __update_repetitions__(repetitions_up, upper_indexes)
            __update_repetitions__(repetitions_down, lower_indexes)

        obj.upper_colors = [PALETTE[repetitions_up.argmax()]]  # 1st
        repetitions_up[repetitions_up.argmax()] = 0
        obj.upper_colors.append(PALETTE[repetitions_up.argmax()])  # 2nd

        obj.lower_colors = [PALETTE[repetitions_down.argmax()]]  # 1st
        repetitions_down[repetitions_down.argmax()] = 0
        obj.lower_colors.append(PALETTE[repetitions_down.argmax()])  # 2nd
