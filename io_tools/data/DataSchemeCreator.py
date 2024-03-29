import os
import sys
from utils.Constants import REPOSITORY_NAME,VIDEOS_DIR,SPRITES_DIR

#Setup the scheme of directories
def setup():
    base_dir="."+os.path.sep
    files=os.listdir(base_dir)
    if REPOSITORY_NAME in files:
        if not os.path.isdir(base_dir+REPOSITORY_NAME):
            print('\033[91m'+"Already exists a file with name \"repository\". We cannot create the base dir called \"repository\", please, modify their name.")
            exit()
        else: return

    #Create dir schema
    print("Creating Repository Base Dir")
    os.makedirs(base_dir+REPOSITORY_NAME) #Create base dir
    os.makedirs(base_dir+REPOSITORY_NAME+os.path.sep+VIDEOS_DIR) #create video dir inside base dir
    with open(base_dir+REPOSITORY_NAME+"/videos.json","w+") as video: #create a file which will store video info
        video.write("[]")

#setup the scheme of directories for a specific sprites of a video
def sprites_dirs_generator(video_path, obj_list):
    sprites_dir = os.path.join(video_path, SPRITES_DIR)
    for obj in obj_list:
        os.makedirs(os.path.join(sprites_dir,str(obj)))