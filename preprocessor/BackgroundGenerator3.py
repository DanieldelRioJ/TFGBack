import cv2
import numpy as np
from objects.Point import Point
from helpers import Helper
import numpy as np

class Backgroundv3:
    def __init__(self, frame_dict):

        self.frame_dict = frame_dict

    def __begin__(self, img):

        self.rows = img.shape[0]
        self.cols = img.shape[1]

        #Todo matrix media
        self.background_array_matrix=[]
        self.n_background_matrix = np.zeros((self.rows,self.cols),dtype=int)

    def upgrade(self, frame_number, img):
        if not hasattr(self, 'background_array_matrix'):
            self.__begin__(img)

        background=img
        if self.frame_dict.get(frame_number) != None:
            for appearance in self.frame_dict.get(frame_number):
                #row,row2, col, col2=Helper.get_points(self.rows, self.cols,appearance.row,appearance.row+appearance.h,appearance.col,appearance.col+appearance.w)
                row, row2, col, col2 = Helper.calculate_new_box(appearance,self.rows, self.cols, 5,5)
                background[row:row2,col:col2]=np.zeros((row2-row,col2-col,3),dtype=np.uint8)
        self.background_array_matrix.append(background)
        gray=cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)
        ret,threshold=cv2.threshold(gray,0,1,cv2.THRESH_BINARY)
        self.n_background_matrix+=threshold

    def get_background(self):
        background=np.zeros((self.rows,self.cols,3),dtype=int)
        for back_aux in self.background_array_matrix:
            background+=back_aux
        #background=[sum(a) for a in self.background_array_matrix]
        n_aux=np.repeat(self.n_background_matrix[:, :, np.newaxis], 3, axis=2)
        background=np.floor_divide(background,n_aux,out=np.zeros_like(background), where=n_aux!=0)

        background=cv2.convertScaleAbs(background)
        aux=background.copy()
        gray=cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)
        ret, threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV)
        background=cv2.inpaint(background, threshold, 10, cv2.INPAINT_TELEA)
        #background= cv2.fastNlMeansDenoisingColored(background, None, 2, 2, 7, 21)
        return background

