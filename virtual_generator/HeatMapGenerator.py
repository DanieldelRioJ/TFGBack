import numpy as np
import cv2

def generateHeatMap(appearances, background):

    shape=background.shape
    mask=np.ones(shape[:-1],int)

    #Iterate over each appearance modifying the general mask (recording number of aparitions)
    for i,appearance in enumerate(appearances[::10]):
        aux_mask=__generate_mask__(appearance,shape)
        mask=np.add(mask,aux_mask)

    #Normalize values to 0-255
    mask=255*mask//np.max(mask)
    mask=mask.astype(np.uint8)
    mask = cv2.GaussianBlur(mask, (21, 21), 15)

    #Convert value mask to real heatmap (rgb)
    heatmap=cv2.applyColorMap(mask,cv2.COLORMAP_JET)
    heatmap=cv2.addWeighted(background,0.6,heatmap,0.4,0)
    return heatmap

def __generate_mask__(appearance,shape):
    mask = np.zeros(shape[:-1], np.uint8)
    mask=cv2.circle(mask, (appearance.center_col, appearance.center_row), (appearance.w+appearance.h)//4, (255), -1, cv2.LINE_AA)
    mask=cv2.GaussianBlur(mask, (11,11), 5)
    return mask
