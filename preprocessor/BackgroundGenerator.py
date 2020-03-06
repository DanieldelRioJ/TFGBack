import cv2
import numpy as np
from objects.Point import Point

class Background:
    def __init__(self, frame_dict, margin_x, margin_y, block_division_size=20, sector_size=20):

        self.block_division_size=block_division_size
        self.frame_dict=frame_dict
        self.sector_size = sector_size
        self.margin_x, self.margin_y = margin_x, margin_y

    def __begin__(self, img):

        self.rows=img.shape[0]
        self.cols=img.shape[1]

        self.background=img

        self.sectors_height = self.rows // self.sector_size
        self.sectors_width = self.cols // self.sector_size

        self.void_squares = []

        if self.frame_dict.get(1) is not None:
            for appearance in self.frame_dict.get(1):
                # self.void_squares.append(((appearance.col, appearance.row), (appearance.col+appearance.w, appearance.row+appearance.h)))
                row1, row2, col1, col2 = calculate_new_box(appearance, self.rows, self.cols, self.margin_x, self.margin_y)
                #self.background[row1:row2, col1:col2] = np.zeros((row2-row1, col2-col1, 3))
                self.void_squares.append(((col1, row1), (col2, row2)))

            """for void_background_part in self.void_squares:
                img = cv2.rectangle(img,void_background_part[0],void_background_part[1], (0, 0, 255), 1)
            cv2.namedWindow('progress', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('progress', 900, 600)
            cv2.imshow("progress", self.background)
            cv2.waitKey()"""

            # breack empty zones into smaller pieces
            new_void_background = []
            for void_background_part in self.void_squares:
                aux = split(void_background_part, self.block_division_size)
                new_void_background.extend(aux)
                aux.clear()
            self.void_squares.clear()
            self.void_squares = new_void_background

            """for void_background_part in self.void_squares:
                pass
                img = cv2.rectangle(img,void_background_part[0],void_background_part[1], (255, 255, 255), 1)
            cv2.namedWindow('progress', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('progress', 900, 600)
            cv2.imshow("progress", self.background)
            cv2.waitKey()"""
            return self.is_completed()
        else: return True

    def is_completed(self):
        return  hasattr(self,'void_squares') and len(self.void_squares) == 0

    def upgrade(self,frame_number,img):

        """for appearance in self.frame_dict.get(frame_number):
            img = cv2.rectangle(img=img, pt1=(appearance.col, appearance.row),
                                pt2=(appearance.col + appearance.w, appearance.row + appearance.h), color=(0, 0, 255),
                                thickness=1)
        cv2.namedWindow('progress', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('progress', 900, 600)
        cv2.imshow("progress", img)
        cv2.waitKey()
"""
        if not hasattr(self,'background'):
            return self.__begin__(img)
        if len(self.void_squares) == 0:
            return True
        if self.frame_dict.get(frame_number) is None:
            for void_square in self.void_squares:
                self.background[void_square[0][1]:void_square[1][1], void_square[0][0]:void_square[1][0]] \
                    = img[void_square[0][1]:void_square[1][1], void_square[0][0]:void_square[1][0]]
            self.void_squares.clear()
            return True

        # check if we can fill empty spaces
        frame_sector_matrix=self.group_map_by_sectors(frame_number)
        empty_now_valid = [void for void in self.void_squares if not self.any_overlap_with_appearances_margins_in_our_sector(
            Point(*void[0]), Point(*void[1]), frame_sector_matrix, self.margin_x, self.margin_y)]
        self.void_squares = [void for void in self.void_squares if void not in empty_now_valid]
        # Fill available empty spaces
        for empty_valid in empty_now_valid:
            self.background[empty_valid[0][1]:empty_valid[1][1], empty_valid[0][0]:empty_valid[1][0]] = img[empty_valid[0][1]:empty_valid[1][1], empty_valid[0][0]:empty_valid[1][0]]
        frame_sector_matrix.clear()

        """cv2.namedWindow('progress', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('progress', 900, 600)
        cv2.imshow("progress",self.background)
        cv2.waitKey(1)"""

        return len(self.void_squares)==0

    def group_map_by_sectors(self, frame_number):
        sector_matrix=[]
        for i in range(self.rows//self.sector_size):
            sector_matrix.append([])
            for j in range(self.cols//self.sector_size):
                sector_matrix[i].append([])

        for appareance in self.frame_dict.get(frame_number):
            sector_col1=appareance.col//self.sector_size
            sector_col2 = (appareance.col+appareance.w) // self.sector_size
            sector_row1 = appareance.row // self.sector_size
            sector_row2 = (appareance.row+appareance.h) // self.sector_size

            #Anhadimos el objeto a todos los sectores en los que aparece.
            for sector_row in range(sector_row1,sector_row2+1):
                for sector_col in range(sector_col1,sector_col2+1):
                    if sector_row < self.sectors_height and sector_col < self.sectors_width:
                        sector_matrix[sector_row][sector_col].append(appareance)
        return sector_matrix

    def get_sectors(self,x1,y1,x2,y2):
        sectors=[]
        sector_col1 = x1 // self.sector_size
        sector_col2 = x2 // self.sector_size
        sector_row1 = y1 // self.sector_size
        sector_row2 = y2 // self.sector_size

        if sector_col1 >= self.sectors_width: return sectors
        if sector_row1 >= self.sectors_height: return sectors
        if sector_col2 >= self.sectors_width: sector_col2 = self.sectors_width - 1
        if sector_row2 >= self.sectors_height: sector_row2 = self.sectors_height - 1

        sectors.append((sector_row1,sector_col1))
        if sector_col2 != sector_col1 and sector_row2 != sector_row1:
            sectors.append((sector_row2, sector_col2))
            sectors.append((sector_row1, sector_col2))
            sectors.append((sector_row2, sector_col1))
        else:
            sectors.append((sector_row2, sector_col2))

        return sectors

    # It tell us if our empty square overlaps with any object considering also the margins and our sector
    def any_overlap_with_appearances_margins_in_our_sector(self, l1, r1, frame_appearances, shape, margin_x=10,
                                                           margin_y=10):

        for sector in self.get_sectors(l1.x, l1.y, r1.x, r1.y):
            try:
                for appearance in frame_appearances[sector[0]][sector[1]]:
                    y1, y2, x1, x2 = calculate_new_box(appearance, self.rows,self.cols, margin_x, margin_y)
                    if do_overlap(l1, r1, Point(x1, y1), Point(x2, y2)):
                        return True
            except IndexError:
                print("Error: Any Overlap")
        return False

#Calculate margins, maybe we are very close to the sides of the screen
def calculate_margins(appearance, rows,cols, margin_horizontal, margin_vertical):
    ml, mr = margin_horizontal, margin_horizontal
    mu, md = margin_vertical, margin_vertical
    if appearance.col < margin_horizontal:
        ml = appearance.col
    if appearance.col + margin_horizontal + appearance.w > cols:
        mr = cols - (appearance.col + appearance.w)
    if appearance.row < margin_vertical:
        mu = appearance.row
    if appearance.row + appearance.h + margin_vertical > rows:
        md = rows - (appearance.row + appearance.h)
    return ml,mr,mu,md

def calculate_new_box(appearance, rows,cols, margin_horizontal, margin_vertical):
    ml, mr, mu, md = calculate_margins(appearance, rows,cols, margin_horizontal, margin_vertical)
    return appearance.row-mu,appearance.row + appearance.h+md,appearance.col-ml,appearance.col + appearance.w+mr



# Returns true if two rectangles(l1, r1)
# and (l2, r2) overlap
def do_overlap(upper_left1, lower_right1, upper_left2, lower_right2):
    # If one rectangle is on left side of other
    if upper_left1.x > lower_right2.x or upper_left2.x > lower_right1.x:
        return False

    # If one rectangle is above other
    # Because on the screen,the value of Y inscreases when the screen is lowered
    if upper_left1.y > lower_right2.y or upper_left2.y > lower_right1.y:
        return False

    return True

"""Split a matrix (just coordinates)into sub-matrices of 'size' size."""
def split(vector, size):
    base_col,base_row,end_col,end_row=vector[0][0],vector[0][1],vector[1][0],vector[1][1]

    height=end_row-base_row
    width=end_col-base_col

    height_parts=height//size
    width_parts=width//size

    rest_height=height%size
    rest_width=width%size

    coordinates=[]
    for i in range(0,width_parts):
        for j in range(0,height_parts):
            coordinates.append(((base_col+size*i,base_row+size*j),(base_col+size*i+size,base_row+size*j+size)))
        if rest_height!=0:
            coordinates.append(((base_col+size*i,end_row-rest_height),(base_col+size*i+size,end_row)))
    if rest_width != 0:
        for j in range(0,height_parts):
            coordinates.append(((end_col-rest_width,base_row+size*j),(end_col,base_row+size*j+size)))
        if rest_height!=0:
            coordinates.append(((end_col-rest_width,end_row-rest_height),(end_col,end_row)))

    return coordinates