import cv2
import numpy as np
from objects.Point import Point
from helpers import Helper
import numpy as np
import scipy


class Backgroundv3:
    def __init__(self, frame_dict):
        self.imgs=[]
        self.frame_dict = frame_dict

    def __begin__(self, img):

        self.rows = img.shape[0]
        self.cols = img.shape[1]

        #Array of images used to generate background
        self.background_array_matrix=[]
        #Matrix counting the number of pixels available in each position (used in mean)
        self.n_background_matrix = np.zeros((self.rows,self.cols),dtype=int)

        #Zeros, at first nothing a
        self.mask=np.zeros((self.rows,self.cols),dtype=np.uint8)

    def upgrade(self, frame_number, img):
        if not hasattr(self, 'background_array_matrix'):
            self.__begin__(img)

        background=img
        #self.imgs.append(img.copy())
        mask=np.ones((self.rows,self.cols),dtype=np.uint8)

        if self.frame_dict.get(frame_number) != None:
            for appearance in self.frame_dict.get(frame_number):
                #row,row2, col, col2=Helper.get_points(self.rows, self.cols,appearance.row,appearance.row+appearance.h,appearance.col,appearance.col+appearance.w)
                row, row2, col, col2 = Helper.calculate_new_box(appearance,self.rows, self.cols, 5,5)
                background[row:row2,col:col2]=np.zeros((row2-row,col2-col,3),dtype=np.uint8)
                mask[row:row2, col:col2] = np.zeros((row2 - row, col2 - col), dtype=np.uint8)
        self.background_array_matrix.append(background)
        #grey=cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)
        ret,threshold=cv2.threshold(mask,0,1,cv2.THRESH_BINARY)
        self.mask = cv2.bitwise_or(self.mask, threshold)
        self.n_background_matrix+=threshold

    def get_background(self):
        background=np.zeros((self.rows,self.cols,3),dtype=int)
        for back_aux in self.background_array_matrix:
            background+=back_aux
        #background=[sum(a) for a in self.background_array_matrix]
        n_aux=np.repeat(self.n_background_matrix[:, :, np.newaxis], 3, axis=2)
        background=np.floor_divide(background,n_aux,out=np.zeros_like(background), where=n_aux!=0)

        background=cv2.convertScaleAbs(background)
        """aux=background.copy()
        gray=cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)
        ret, threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV)

        #result, histogram_mask = self.__get_mask_mode_pixels__()
        result, histogram_mask = self.__get_mask_mode_pixels_v2__()

        self_mask=cv2.bitwise_not(self.mask*255)

        cv2.imshow("self mask", self_mask)
        cv2.waitKey()

        cv2.imshow("histogram mask", histogram_mask)
        cv2.waitKey()

        copy_mask=cv2.bitwise_and(self_mask,histogram_mask)
        cv2.imshow("copy mask", copy_mask)
        cv2.waitKey()
        histogram_mask=cv2.bitwise_not(histogram_mask)
        impaint_mask=cv2.bitwise_and(histogram_mask,self_mask)
        cv2.imshow("impaint mask", impaint_mask)
        cv2.waitKey()

        background[np.where(copy_mask==255)]=result[np.where(copy_mask==255)]
        cv2.imshow("background", background)
        cv2.waitKey()"""

        background=cv2.inpaint(background,cv2.bitwise_not(self.mask*255) , 30, cv2.INPAINT_TELEA)
        #background= cv2.fastNlMeansDenoisingColored(background, None, 2, 2, 7, 21)
        return background

    def __get_mask_mode_pixels__(self):

        def function(row):
            row = row.reshape(1, len(row))
            hist = cv2.calcHist(row, [0], None, [16], [0, 16])
            max_color = np.argmax(hist)  # Index of the most repeated value
            max_quantity = max(hist)[0]  # Most repeated quantity
            hist[max_color] = -1
            second_max_quantity = max(hist)[0]  # Second Most repeated quantity
            if second_max_quantity * 2 < max_quantity:  # If the difference is big, consider it, else, return -1
                return np.uint8(max_color)
            return np.uint8(255)

        images = np.array(self.imgs) // 16  # Reduce color from 255 to 16 poxible values per color (reduce quality, but also noise).
        cv2.imshow("fdfsd", images[0])
        cv2.waitKey()
        new_array = np.apply_along_axis(function, 0, images)


        channels = cv2.split(new_array)

        masks = [cv2.threshold(channel, 254, 255, cv2.THRESH_BINARY_INV) for channel in
                 channels]  # Create mask for eaach channel. It mask invalid values

        mask = cv2.bitwise_and(masks[0][1], masks[1][
            1])  # second element of the mask, remember, threshold return 2 values, second is the mask
        mask = cv2.bitwise_and(mask, masks[2][1])

        new_array = cv2.bitwise_and(new_array, new_array, mask=mask)

        return new_array*16, mask


