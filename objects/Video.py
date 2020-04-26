class Video(object):
    def __init__(self, id, upload_date, recorded_date, frame_quantity=-1, fps=-1,title=None,city=None,description=None, processed=False,original_filename=None):
        self.id = id
        self.upload_date = upload_date
        self.recorded_date = recorded_date
        self.frame_quantity = frame_quantity
        self.fps = fps
        self.processed = processed
        self.title=title
        self.city=city
        self.description=description
        self.original_filename=original_filename

    def set_perspective(self,points):
        self.perspective={"points":points,'limits':{None}}