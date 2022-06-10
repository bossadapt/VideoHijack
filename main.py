import math
import os
import time
import pyvirtualcam
import argparse
import threading
import numpy as np
from PIL import Image
from tkinter import ttk, filedialog, messagebox, Tk, Entry
import cv2

killThread = False
currentWorkSpace = os.getcwd()
videoStorage = "videosToFrames"
framerate = 30

def makeVideoStorage():
    if videoStorage in os.listdir("."):
        pass
    else:
        os.mkdir(videoStorage)

def listVideoNames():
    os.chdir(videoStorage)
    list = os.listdir(".")
    os.chdir(currentWorkSpace)
    return list

def startGUI():
    global root
    root = Tk()
    root.title("Video Hijack")
    frm = ttk.Frame(root, padding=10)
    frm.grid()
    ttk.Label(frm, text="Video Hijack").grid(column=0, row=0)
    ttk.Button(frm, text="Add Video", command=addVideo).grid(column=1, row=0)
    ttk.Button(frm, text="Live Video", command=playLiveThread).grid(column=2, row=0)
    global frameInput
    frameInput = Entry(frm,width=10)
    frameInput.insert(0, "30")
    frameInput.grid(column=3, row=0)
    currentSpot = 1
    videoList = []
    videoCount = 0
    for item in listVideoNames():
        if item != ".idea" and item != "main.py" and item != "venv":
            videoList.append(item)
            ttk.Label(frm, text=item).grid(column=0, row=currentSpot)
            ttk.Button(frm,
                       text="Play Once", command=lambda videoCount=videoCount: playVideoThread(currentWorkSpace+"/"+videoStorage+"/"+videoList[videoCount],False)).grid(column=1, row=currentSpot)
            ttk.Button(frm,
                       text="Play Loop", command=lambda videoCount=videoCount: playVideoThread(
                    currentWorkSpace + "/" + videoStorage + "/" + videoList[videoCount], True)).grid(column=2,
                                                                                                   row=currentSpot)
            ttk.Button(frm,
                       text="Remove", command=lambda videoCount=videoCount: removeVideo(currentWorkSpace+"/"+videoStorage+"/"+videoList[videoCount])).grid(column=3, row=currentSpot)
            videoCount = videoCount + 1
        currentSpot = currentSpot + 1
    root.mainloop()

def refreshGui():
    root.destroy()
    startGUI()

def removeVideo(video):
    try:
        os.remove(video)
        os.rmdir(video)
    except:
        messagebox.showinfo("Error", "Need to run this application in admin to delete files")


def addVideo():
    filename = filedialog.askopenfilename(initialdir=currentWorkSpace,
                                          title="Select a File",
                                          filetypes=(("Video files", "*.*"),
                                                     ("all files", "*.*")))
    #pull name out of file name
    name = filename
    while "/" in name:
        indexOfSlash = name.index("/")
        name = name[indexOfSlash+1:]
    indexOfPeriod = name.index(".")
    name = name[:indexOfPeriod]
    #check if the file has been done already
    directoryList = listVideoNames()
    if name in directoryList:
        messagebox.showinfo("Error", "A file with this name already has been added")
    else:
        videoToFramesFile(name, filename)
        refreshGui()




def playLiveCam():
    parser = argparse.ArgumentParser()
    parser.add_argument("--camera", type=int, default=0, help="ID of webcam device (default: 0)")
    parser.add_argument("--fps", action="store_true", help="output fps every second")
    args = parser.parse_args()
    vc = cv2.VideoCapture(args.camera, cv2.CAP_DSHOW)
    if not vc.isOpened():
        raise RuntimeError('Could not open video source')
    pref_width = 1280
    pref_height = 720
    pref_fps_in = 30
    vc.set(cv2.CAP_PROP_FRAME_WIDTH, pref_width)
    vc.set(cv2.CAP_PROP_FRAME_HEIGHT, pref_height)
    vc.set(cv2.CAP_PROP_FPS, pref_fps_in)
    # Query final capture device values (maybe different from preferred settings).
    width = int(vc.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps_in = vc.get(cv2.CAP_PROP_FPS)
    with pyvirtualcam.Camera(width, height, fps_in, fmt=pyvirtualcam.PixelFormat.BGR, print_fps=args.fps) as cam:
        while True:
            # Read frame from webcam.
            ret, frame = vc.read()
            cam.send(frame)
            cam.sleep_until_next_frame()
            if killThread:
                cv2.destroyAllWindows()
                break

def videoToFramesFile(filename, video):
    os.chdir("videosToFrames")
    os.mkdir(filename)
    os.chdir(filename)
    vidcap = cv2.VideoCapture(video)
    success, image = vidcap.read()
    count = 0
    messagebox.showinfo("Notice", "Turning video to frames and saving. Please wait until finished")
    while success:
        cv2.imwrite("%d.jpg" % count, image)  # save frame as JPEG file
        success, image = vidcap.read()
        count += 1
    os.chdir(currentWorkSpace)

def playLiveThread():
    global killThread
    killThread = True
    time.sleep(0.1)
    killThread = False
    camThread = threading.Thread(target=playLiveCam)
    camThread.setDaemon(True)
    camThread.start()


def playVideoThread(videoName, Loop):
    global killThread
    global loop
    framePerSec = frameInput.get()
    try:
        framePerSec = int(framePerSec)
    except:
        messagebox.showinfo("Warning", "frame rate not set to int defaulted to 30FPS")
        framePerSec = 30
    loop = Loop
    killThread = True
    time.sleep(math.ceil(1/framePerSec))
    killThread = False
    print("FPS:", framePerSec)
    camThread = threading.Thread(target=playVideo, args=(videoName, framePerSec))
    camThread.setDaemon(True)
    camThread.start()

def playVideo(videoName, framePerSec):
    img = Image.open(videoName + "\\1.jpg")
    width = img.width
    height = img.height

    with pyvirtualcam.Camera(width=width, height=height, fps=framePerSec) as cam:
        count = 0
        while (os.path.exists(videoName + "\\" + str(count) + ".jpg")):
            currentFrame = np.array(Image.open(videoName + "/" + str(count) + ".jpg"))
            cam.send(currentFrame)
            cam.sleep_until_next_frame()
            count = count + 1
            if not os.path.exists(videoName + "\\" + str(count+1) + ".jpg") and loop:
                count = 0
            if killThread:
                cv2.destroyAllWindows()
                break



if __name__ == '__main__':
    makeVideoStorage()
    startGUI()

