def get_video_instance(name, annotations_filename,date_uploaded, date_recorded, obj_number, frame_number=None, fps=None):
    return {'name': name,
            'annotations_filename':annotations_filename,
            'processed':False,
            'date_uploaded': date_uploaded,
            'date_recorded': date_recorded,
            'obj_number': obj_number,
            'frame_number': obj_number,
            'fps': fps}
