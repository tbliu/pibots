from picamera.array import PiRGBArray
from picamera import PiCamera
import datetime
import time
import cv2
import os
import send_sms as sms
import upload as flickr
from multiprocessing import Process

"""
Reference:
    https://hackernoon.com/raspberrypi-home-surveillance-with-only-150-lines-of-python-code-2701bd0373c9
"""

# Cleaning up images folder
folder = "./images"
for File in os.listdir(folder):
    path = os.path.join(folder, File)
    try:
        if os.path.isfile(path):
            os.unlink(path)
    except Exception as e:
        print(e)

# Initialization
camera = PiCamera()
camera.rotation = 180
camera.resolution = (640, 480)
camera.framerate = 16
rawCapture = PiRGBArray(camera, size=(640, 480))
firstFrame = None
currFrame = None
proc = None
counter = 0
timeBuffer = 2 # amount of time before camera takes another picture
lastTime = datetime.datetime.now()

# Warming up camera
print("Waking up...")
time.sleep(1) # give the camera 1 second to initialize

# Image processing
for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    frame = f.array
    currFrame = f.array
    timestamp = datetime.datetime.now()
    status = "Unoccupied"

    # Convert frame to grayscale for processing
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    # Initialize background reference
    if firstFrame is None:
        print("Finding background...")
        firstFrame = gray.copy().astype("float")
        cv2.accumulateWeighted(gray, firstFrame, 0.5)
        cv2.imwrite("./images/background.jpg", frame)
        rawCapture.truncate(0)
        print("Recording!")
        continue
    
    # Find the difference between frames
    frameDiff = cv2.absdiff(gray, cv2.convertScaleAbs(firstFrame))
    cv2.accumulateWeighted(gray, firstFrame, 0.5)
    _, thresh = cv2.threshold(frameDiff, 25, 255, cv2.THRESH_BINARY)
    thresh = cv2.dilate(thresh, None, iterations=2)
    
    # Find contours
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    for c in cnts:
        if cv2.contourArea(c) < 5000:
            continue
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        status = "Occupied"
        
        cv2.putText(frame, "Room Status: {}".format(status), (10,20), \
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(frame, timestamp.strftime("%A %d %B %Y %I:%M:%S%p"), \
                (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
    cv2.putText(frame, "Room Status: {}".format(status), (10,20), \
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, timestamp.strftime("%A %d %B %Y %I:%M:%S%p"), \
            (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
    cv2.imwrite("./static/LiveFeed.jpg", currFrame)

    # Take an image of whatever is moving in frame
    if status == "Occupied":
        fileName = "./images/securitycam_{}.jpg".format(counter)
        p_write = Process(target=cv2.imwrite(fileName, frame), args=(fileName, frame))
        print("Taking picture!")
        if (timestamp - lastTime).seconds >= timeBuffer:
            counter += 1
            lastTime = timestamp
            """
            p_msg = Process(target=sms.send_msg(), args=())
            p_msg.start()
            p_msg.join()
   
            p_upload = Process(target=flickr.upload(fileName), args=(fileName))
            p_upload.start()
            p_upload.join()
            """  
    rawCapture.truncate(0)

camera.release()
cv2.destroyAllWindows()
