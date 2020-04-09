from shapely.geometry import Polygon

def do_filter(object_list,area_filter):
    if area_filter==None or area_filter.get('area')==None:
        return object_list

    area=create_polygon_with_coordinates(area_filter['area'])

    aux_object_list={}
    for obj_id in object_list:
        obj=object_list[obj_id]
        for appearance in obj.appearances:
            list=[(appearance.col,appearance.row),(appearance.col+appearance.w, appearance.row),
                                       (appearance.col, appearance.row+appearance.h),(appearance.col+appearance.w,appearance.row+appearance.h)]
            appearance_square=Polygon(list)
            if appearance_square.intersects(area):
                aux_object_list[obj_id]=obj
                break
    return aux_object_list

def create_polygon_with_coordinates(coordinates_array):
    return Polygon([(coordinate['x'],coordinate['y']) for coordinate in coordinates_array])