import math

def do_filter(object_list, path_filter):
    range=100 #20pixels max between filter path and real path
    path=path_filter.get('path')
    if path is None or path_filter is None:
        return object_list
    aux_list={}
    for obj_id in object_list:
        obj=object_list.get(obj_id)
        i=0
        for appearance in obj.appearances:
            #if distance_between_points(appearance.center_col,appearance.center_row,path[i]['x'],path[i]['y'])<range:
            if point_inside_square(path[i]['x'],path[i]['y'],appearance.col,appearance.row, appearance.col+appearance.w, appearance.row+appearance.h):
                i+=1
                if i==len(path): #if the objects match the path provided
                    aux_list[obj_id]=obj
                    break

    return aux_list

#Arguments: Point coordinates, square coordinates(upperleft coordinates, bottomright coordinates)
def point_inside_square(col,row, coll,rowl,colr,rowr):
    return coll<=col and colr>=col and rowl<=row and rowr>=row

def distance_between_points(col1,row1,col2,row2):
    row=row1-row2
    col=col1-col2
    return math.sqrt(row**2+col**2)