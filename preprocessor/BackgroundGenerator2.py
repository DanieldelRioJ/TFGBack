import cv2
import numpy as np
from objects.Point import Point
from helpers import Helper
import numpy as np

class Backgroundv2:
    def __init__(self, frame_dict, sector_size=20):

        self.frame_dict = frame_dict
        self.sector_size = sector_size

    def __begin__(self, img):

        self.rows = img.shape[0]
        self.cols = img.shape[1]

        #Todo matrix media
        self.background_matrix=np.zeros(img.shape,dtype=np.uint16)
        self.n_background_matrix = np.zeros((self.rows,self.cols),dtype=int)

        self.sectors_height = self.rows // self.sector_size
        self.sectors_width = self.cols // self.sector_size

    def __add_value_to_pixel__(self,value,col,row):
        #print(f"{row} {col}")
        n_images_processed=self.n_background_matrix[row][col]
        (x,y,z)=(self.background_matrix[row][col] * n_images_processed + value) // (n_images_processed + 1)
        """x = (self.background_matrix[row][col][0] + value[0]) // 2
        y = (self.background_matrix[row][col][1] + value[1]) // 2
        z = (self.background_matrix[row][col][2] + value[2]) // 2"""
        self.n_background_matrix[row][col]=n_images_processed+1
        return (x,y,z)

    def upgrade(self, frame_number, img):
        """for appearance in self.frame_dict.get(frame_number):
            img = cv2.rectangle(img=img, pt1=(appearance.col, appearance.row),
                                pt2=(appearance.col + appearance.w, appearance.row + appearance.h), color=(0, 0, 255),
                                thickness=1)
        cv2.namedWindow('progress', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('progress', 900, 600)
        cv2.imshow("progress", img)
        cv2.waitKey()
"""
        if not hasattr(self, 'background_matrix'):
            self.__begin__(img)

        sector_matrix=self.group_map_by_sectors(frame_number)

        """self.background_matrix=[
            [self.__add_value_to_pixel__(pix,col,row) for col, pix in enumerate(img[row]) if not self.pixel_inside_object(col,row,sector_matrix)]
            for row,lista in enumerate(img)
        ]"""
        for i in range(0,len(self.background_matrix)):
            for j in range(0,len(self.background_matrix[0])):
                if not self.pixel_inside_object(j,i,sector_matrix):
                    self.background_matrix[i][j]=self.__add_value_to_pixel__(img[i][j],j,i)
                    pass
        back=cv2.convertScaleAbs(self.background_matrix)
        cv2.imwrite(str(frame_number)+".jpg",back)
        """cv2.namedWindow('progress', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('progress', 900, 600)
        cv2.imshow("progress",back)
        cv2.waitKey()"""

    def group_map_by_sectors(self, frame_number):
        sector_matrix = []
        for i in range(self.rows // self.sector_size):
            sector_matrix.append([])
            for j in range(self.cols // self.sector_size):
                sector_matrix[i].append([])

        for appareance in self.frame_dict.get(frame_number):
            sector_col1 = appareance.col // self.sector_size
            sector_col2 = (appareance.col + appareance.w) // self.sector_size
            sector_row1 = appareance.row // self.sector_size
            sector_row2 = (appareance.row + appareance.h) // self.sector_size

            # Anhadimos el objeto a todos los sectores en los que aparece.
            for sector_row in range(sector_row1, sector_row2 + 1):
                for sector_col in range(sector_col1, sector_col2 + 1):
                    if sector_row < self.sectors_height and sector_col < self.sectors_width:
                        sector_matrix[sector_row][sector_col].append(appareance)
        return sector_matrix

    # Get sector of a pixel
    def get_sector(self, col, row):
        sector_col = col // self.sector_size
        sector_row = row // self.sector_size
        return sector_row, sector_col

    # It tell us if our the pixel is inside any object
    def pixel_inside_object(self, col, row, frame_appearances):
        if frame_appearances == None:
            return False
        sector = self.get_sector(col, row)
        if len(frame_appearances[sector[0]][sector[1]]) != 0:
            return True
        return False
        try:
            for appearance in frame_appearances[sector[0]][sector[1]]:
                if Helper.pixel_inside(col, row, Point(appearance.col, appearance.row), Point(appearance.col+appearance.w, appearance.row+appearance.h)):
                    return True
        except IndexError:
            print("Error: Any Overlap")
        return False
