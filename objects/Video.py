class Video(object):
    def __init__(self, name, filename, annotations_filename, upload_date, recorded_date, frame_quantity=-1, fps=-1,
                 processed=False):
        self.name = name
        self.filename = filename
        self.annotations_filename = annotations_filename
        self.upload_date = upload_date
        self.recorded_date = recorded_date
        self.frame_quantity = frame_quantity
        self.fps = fps
        self.processed = processed
