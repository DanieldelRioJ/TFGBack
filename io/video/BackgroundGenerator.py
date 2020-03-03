import math

import cv2
import numpy as np

#Calculate margins, maybe we are very close to the sides of the screen
def calculate_margins(appearance, shape, margin_horizontal, margin_vertical):
    ml, mr = margin_horizontal, margin_horizontal
    mu, md = margin_vertical, margin_vertical
    if appearance.x < margin_horizontal:
        ml = appearance.x
    if appearance.x + margin_horizontal + appearance.w > shape[1]:
        mr = shape[1] - (appearance.x + appearance.w)
    if appearance.y < margin_vertical:
        mu = appearance.y
    if appearance.y + appearance.h + margin_vertical > shape[0]:
        md = shape[0] - (appearance.y + appearance.h)
    return ml,mr,mu,md

def calculate_new_box(appearance, shape, margin_horizontal, margin_vertical):
    ml, mr, mu, md = calculate_margins(appearance, shape, margin_horizontal, margin_vertical)
    return appearance.y-mu,appearance.y + appearance.h+md,appearance.x-ml,appearance.x + appearance.w+mr


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Returns true if two rectangles(l1, r1)
# and (l2, r2) overlap
def do_overlap(l1, r1, l2, r2):
    # If one rectangle is on left side of other
    if l1.x > r2.x or l2.x > r1.x:
        return False

    # If one rectangle is above other
    # Because on the screen,the value of Y inscreases when the screen is lowered
    if l1.y > r2.y or l2.y > r1.y:
        return False

    return True

#It tell us if our empty square overlaps with any object considering also the margins
def any_overlap_with_appearances_margins(l1,r1,appearances,shape,margin_x=10,margin_y=10):
    for appearance in appearances:
        y1, y2, x1, x2 = calculate_new_box(appearance, shape, margin_x, margin_y)
        if do_overlap(l1,r1,Point(x1,y1),Point(x2,y2)):
            return True
    return False

#It tell us if our empty square overlaps with any object
def any_overlap(l1,r1,appearances):
    for appearance in appearances:
        if do_overlap(l1,r1,Point(appearance.x,appearance.y),Point(appearance.x+appearance.w,appearance.y+appearance.h)):
            return True
    return False

"""
Margin: the margin of the elements clipping to generate background
"""
def backgroundCreator(map, imgs, margin_x, margin_y, block_division_size=50):
    shape=imgs[0].shape
    void_background=[] #stores black squares coordinates which need to be filled
    background = imgs[0].copy() #stores background image, based on first frame

    if map.get(1) is not None:
        for appearance in map.get(1):
            y1,y2,x1,x2=calculate_new_box(appearance,shape,margin_x,margin_y)
            #background[y1:y2, x1:x2] = np.zeros((y2-y1, x2-x1, 3))
            void_background.append((x1,x2,y1,y2))

        # breack empty zones into smaller pieces
        new_void_background = []
        for void_background_part in void_background: 
            aux=split(void_background_part,block_division_size)
            new_void_background.extend(aux)
            aux.clear()
        void_background.clear()
        void_background=new_void_background

        frame_number=1
        for img in imgs[1:]:
            frame_number+=1
            print(frame_number)
            if len(void_background)==0:
                break
            if map.get(frame_number) is None:
                for void_square in void_background:
                    background[void_square[2]:void_square[3],void_square[0],void_square[1]]\
                        =img[void_square[2]:void_square[3],void_square[0],void_square[1]]
                void_background.clear()
                break

            #check if we can fill empty spaces
            empty_now_valid=[void for void in  void_background if not any_overlap_with_appearances_margins(
                Point(void[0],void[2]), Point(void[1],void[3]),map.get(frame_number),shape, margin_x,margin_y)]
            void_background=[void for void in void_background if void not in empty_now_valid]
            #Fill available empty spaces
            for empty_valid in empty_now_valid:
                background[empty_valid[2]:empty_valid[3],empty_valid[0]:empty_valid[1]]=img[empty_valid[2]:empty_valid[3],empty_valid[0]:empty_valid[1]]

    return background

"""Split a matrix into sub-matrices of 'size' size."""
def split(vector, size):
    base_x,base_y,end_x,end_y=vector[0],vector[2],vector[1],vector[3]
    height,width=end_x-base_x,end_y-base_y
    height_partial,width_partial=height//size,width//size
    rest_height,rest_width=height%size,width%size
    coordinates=[]
    for i in range(0,height_partial):
        for j in range(0,width_partial):
            coordinates.append((base_x+size*i,base_x+size*i+size,base_y+size*j,base_y+size*j+size))
        if rest_width!=0:
            coordinates.append((base_x+size*i,base_x+size*i+size,end_y-rest_width,end_y))
    if rest_height != 0:
        for j in range(0,width_partial):
            coordinates.append((end_x-rest_height,end_x,base_y+size*j,base_y+size*j+size))
        if rest_width!=0:
            coordinates.append((end_x-rest_height,end_x,end_y-rest_width,end_y))
    return coordinates

class Background:
    def __init__(self,map,img, margin_x, margin_y, block_division_size=10,sector_size=20):
        self.background=img

        self.map=map
        self.shape=img.shape

        self.sector_size = sector_size
        self.sectors_height = self.shape[0]//self.sector_size
        self.sectors_width = self.shape[1] // self.sector_size

        self.margin_x,self.margin_y=margin_x,margin_y
        self.void_squares=[]
        if map.get(1) is not None:
            for appearance in map.get(1):
                y1, y2, x1, x2 = calculate_new_box(appearance, self.shape, margin_x, margin_x)
                #background[y1:y2, x1:x2] = np.zeros((y2-y1, x2-x1, 3))
                self.void_squares.append((x1, x2, y1, y2))

            # breack empty zones into smaller pieces
            new_void_background = []
            for void_background_part in self.void_squares:
                aux = split(void_background_part, block_division_size)
                new_void_background.extend(aux)
                aux.clear()
            self.void_squares.clear()
            self.void_squares = new_void_background
            self.group_map_by_sectors()

    def is_completed(self):
        return len(self.void_squares) == 0

    def upgrade(self,imgs):
        frame_number = 1
        for img in imgs:
            frame_number += 1
            print(frame_number)
            if len(self.void_squares) == 0:
                break
            if self.map.get(frame_number) is None:
                for void_square in self.void_squares:
                    self.background[void_square[2]:void_square[3], void_square[0], void_square[1]] \
                        = img[void_square[2]:void_square[3], void_square[0], void_square[1]]
                self.void_squares.clear()
                break

            # check if we can fill empty spaces
            empty_now_valid = [void for void in self.void_squares if not self.any_overlap_with_appearances_margins_in_our_sector(
                Point(void[0], void[2]), Point(void[1], void[3]), self.map.get(frame_number), self.shape, self.margin_x, self.margin_y)]
            self.void_squares = [void for void in self.void_squares if void not in empty_now_valid]
            # Fill available empty spaces
            for empty_valid in empty_now_valid:
                self.background[empty_valid[2]:empty_valid[3], empty_valid[0]:empty_valid[1]] = img[empty_valid[2]:empty_valid[3],empty_valid[0]:empty_valid[1]]

            cv2.namedWindow('progress', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('progress', 900, 600)
            cv2.imshow("progress",self.background)
            cv2.waitKey(1)
        return len(self.void_squares)==0

    def group_map_by_sectors(self):

        map=self.map.copy()
        self.map={}
        for frame in map:
            sector_matrix=[]
            for i in range(self.shape[0]//self.sector_size):
                sector_matrix.insert(i,[])
                for j in range(self.shape[1]//self.sector_size):
                    sector_matrix[i].insert(j,[])

            for appareance in map.get(frame):
                sector_x1=appareance.x//self.sector_size
                sector_x2 = (appareance.x+appareance.w) // self.sector_size
                sector_y1 = appareance.y // self.sector_size
                sector_y2 = (appareance.y+appareance.h) // self.sector_size
                if(sector_x2>self.sectors_width):sector_x2=self.sectors_width-1
                if (sector_y2 > self.sectors_height): sector_y2 = self.sectors_height - 1
                try:
                    sector_matrix[sector_y1][sector_x1].append(appareance)
                    if sector_x2==sector_x1 and sector_y2==sector_y1:
                        continue
                    elif sector_x2!=sector_x1 and sector_y2 != sector_y1:
                        sector_matrix[sector_y2][sector_x2].append(appareance)
                        sector_matrix[sector_y1][sector_x2].append(appareance)
                        sector_matrix[sector_y2][sector_x1].append(appareance)
                        continue
                    else:
                        sector_matrix[sector_y2][sector_x2].append(appareance)
                except IndexError: #Happens when a gt box is partial outside the screen, so those points are not inside any sector
                    print(f"Error: id:{appareance.object.id} frame:{appareance.frame}, ({appareance.x},{appareance.y}),({appareance.x+appareance.w},{appareance.y+appareance.h})")
                    pass
            self.map[frame]=sector_matrix

    def get_sectors(self,x1,y1,x2,y2):
        sectors=[]
        sector_x1 = x1 // self.sector_size
        sector_x2 = x2 // self.sector_size
        sector_y1 = y1 // self.sector_size
        sector_y2 = y2 // self.sector_size

        if sector_x2 > self.sectors_width: sector_x2 = self.sectors_width - 1
        if sector_y2 > self.sectors_height: sector_y2 = self.sectors_height - 1

        sectors.append((sector_y1,sector_x1))
        if sector_x2 != sector_x1 and sector_y2 != sector_y1:
            sectors.append((sector_y2, sector_x2))
            sectors.append((sector_y1, sector_x2))
            sectors.append((sector_y2, sector_x1))
        else:
            sectors.append((sector_y2, sector_x2))

        return sectors


    #It tell us if our empty square overlaps with any object considering also the margins and our sector
    def any_overlap_with_appearances_margins_in_our_sector(self,l1,r1,frame_appearances,shape,margin_x=10,margin_y=10):

        for sector in self.get_sectors(l1.x,l1.y,r1.x,r1.y):
            try:
                for appearance in frame_appearances[sector[0]][sector[1]]:
                    y1, y2, x1, x2 = calculate_new_box(appearance, shape, margin_x, margin_y)
                    if do_overlap(l1,r1,Point(x1,y1),Point(x2,y2)):
                        return True
            except IndexError:
                pass
        return False