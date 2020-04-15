import math
import os
import re
from shapely.geometry import Polygon

#get iou of 2 boxes
#intersection = common area
#union = A area plus B area minus intersection
def get_iou(upper_left1, lower_right1, upper_left2, lower_right2):
    if do_overlap(upper_left1, lower_right1, upper_left2, lower_right2):
        intersection_area=(min(lower_right1.x,lower_right2.x)
                      -max(upper_left1.x, upper_left2.x))\
                     *(min(lower_right1.y, lower_right2.y)
                       -max(upper_left1.y, upper_left2.y))

        #Supossing coordinates always positive (no need of abs)
        a_area=area(upper_left1,lower_right1)
        b_area=area(upper_left2,lower_right2)
        return intersection_area/(a_area+b_area-intersection_area)
    else:
        return 0

def area(upper_left, lower_right):
    return (lower_right.x-upper_left.x)*(lower_right.y-upper_left.y)

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

def pixel_inside(col,row, upper_left,lower_right):
    if col<upper_left.x or col > lower_right.x:
        return False
    elif row<upper_left.y or row > lower_right.y:
        return False
    return True

#Make sure that the gt is not outside of the screen
def get_points(rows, cols,row1,row2,col1,col2):

    #The col1 and row1 is always inside (Look at MOTParser implementation)
    #However, row2 and col2 are not checked on MOTParser because there we dont know the resolution of the video.

    if row2>rows:
        row2=rows
    if col2>cols:
        col2=cols
    return row1,row2,col1,col2

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

def convert_frame_map_to_object_map(frame_map, object_list):
    new_object_map={}
    for obj_id in object_list:
        obj=object_list.get(obj_id)
        del obj.appearances
        obj.appearances=[]
        new_object_map[obj_id]=obj

    for frame_id in frame_map:
        for appearance in frame_map.get(frame_id):
            new_object_map.get(appearance.object.id).appearances.append(appearance)

    return new_object_map

def distance(x1:int,y1:int,x2:int,y2:int):
    x,y=x1-x2,y1-y2
    return math.sqrt((x**2)+(y**2))

#Get file chunk
def get_chunk(full_path,range_header):
    byte1, byte2 = 0, None
    if range_header:
        match = re.search(r'(\d+)-(\d*)', range_header)
        groups = match.groups()

        if groups[0]:
            byte1 = int(groups[0])
        if groups[1]:
            byte2 = int(groups[1])

    file_size = os.stat(full_path).st_size
    start = 0
    length = 102400

    if byte1 < file_size:
        start = byte1
    if byte2:
        length = byte2 + 1 - byte1
    else:
        length = file_size - start

    with open(full_path, 'rb') as f:
        f.seek(start)
        chunk = f.read(length)
    return chunk, start, length, file_size

def get_polygon_by_appearance(apperance):
    return Polygon([(apperance.col,apperance.row),(apperance.col+apperance.w,apperance.row),
                   (apperance.col+apperance.w,apperance.row+apperance.h),(apperance.col,apperance.row+apperance.h)])