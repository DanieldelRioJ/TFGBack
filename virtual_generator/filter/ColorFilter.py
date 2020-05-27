import math
from utils.Constants import COLOR_DIFERENCE_LIMIT
from helpers import Helper
def do_filter(object_list, color_filter):
    if color_filter is None:
        return object_list

    upper_color_param=color_filter.get('upper_color')
    lower_color_param=color_filter.get('lower_color')
    if upper_color_param is None and lower_color_param is None:
        return object_list

    new_obj_list={}

    for id,obj in object_list.items():
        if (upper_color_param is None or __any_color__(obj.upper_colors,upper_color_param)) and \
                (lower_color_param is None or __any_color__(obj.lower_colors,lower_color_param)):
            new_obj_list[id]=obj
    return new_obj_list

def __any_color__(colors_array,color_param):
    for color in colors_array:
        if color['name']==color_param:
            return True
    return False

"""def __hex_to_rgb(hex):
    hex=hex.lstrip('#')
    return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))"""

