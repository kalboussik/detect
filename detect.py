import cv2
import numpy as np
from keras.models import load_model
import time
import os
from stream import start_stream, stop_stream
from settings import start_delay,stop_delay,cam 

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]



# Disable OAuthlib's HTTPS verification when running locally.
# *DO NOT* leave this option enabled in production.
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "0"

api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "code.json"

# Get credentials and create an API client
flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
    client_secrets_file, scopes)
credentials = flow.run_local_server()
youtube = googleapiclient.discovery.build(
    api_service_name, api_version, credentials=credentials)

# Load the model
model = load_model('./keras_model.h5')

# CAMERA can be 0 or 1 based on default camera of your computer.

RTSP_URL = cam
os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;udp'

camera = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)

camera = cv2.VideoCapture(1)


if not camera.isOpened():
    print('Cannot open RTSP stream')
    exit(-1)

# Grab the labels from the labels.txt file. This will be used later.
labels = open('labels.txt', 'r').readlines()
pos_count = 0
neg_count = 0
flag = "pause"
current = time.time()
ID=0
while True:
    try:	
        # Grab the webcameras image.
        ret, image = camera.read()
        # Resize the raw image into (224-height,224-width) pixels.
        image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)
        # Show the image in a window
        #cv2.imshow('Cam', image)
        # Make the image a numpy array and reshape it to the models input shape.
        image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)
        # Normalize the image array
        image = (image / 127.5) - 1
        # Have the model predict what the current image is. Model.predict
        # returns an array of percentages. Example:[0.2,0.8] meaning its 20% sure
        # it is the first label and 80% sure its the second label.
        if (time.time() - current) >= 1 :
            current = time.time()
            probabilities = model.predict(image)
            # Print what the highest value probabilitie label
            #print("++++++++++++++++++++++++++++++++")
            #print(np.argmax(probabilities))
            if (np.argmax(probabilities) == 1 and flag=="pause") :
                if (pos_count >= start_delay) :
                    print("body present live stream begin")
                    flag = "streaming"
                    pos_count=0
                    ID = start_stream(cam,youtube)
                else:
                    pos_count=pos_count+1
                    print(pos_count)

            elif (np.argmax(probabilities) == 0 and flag=="pause") :
                pos_count=0

            elif (np.argmax(probabilities) == 0 and flag=="streaming") :
                if (neg_count >= stop_delay) :
                    print("body absent stop stream")
                    flag = "pause"
                    neg_count=0
                    ok = stop_stream(youtube,ID)

                else:
                    neg_count=neg_count+1
                    flag="streaming"
                    print(neg_count)
                    
            elif (np.argmax(probabilities) == 1 and flag=="streaming") :
                neg_count=0
        # Listen to the keyboard for presses.
        keyboard_input = cv2.waitKey(1)
        # 27 is the ASCII for the esc key on your keyboard.
        if keyboard_input == 27:
            break
    except Exception as e:
        print(e)

camera.release()
cv2.destroyAllWindows()


