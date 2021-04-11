# Import packages
import os,datetime
import argparse
import cv2
import numpy as np
import sys
import time
from threading import Thread
import importlib.util
from ..common.telegram_send import Send_Telegram , carga_evento
from ..models import MedioNotificacion,Eventos
from flask import current_app


class VideoStream:
    """Camera object that controls video streaming"""
    def __init__(self,resolution=(800,600),framerate=30,link=''):
        # Initialize the PiCamera and the camera image stream
        self.stream = cv2.VideoCapture(link)
        ret = self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        ret = self.stream.set(3,resolution[0])
        ret = self.stream.set(4,resolution[1])
            
        # Read first frame from the stream
        (self.grabbed, self.frame) = self.stream.read()

    # Variable to control when the camera is stopped
        self.stopped = False

    def start(self):
    # Start the thread that reads frames from the video stream
        Thread(target=self.update,args=()).start()
        return self

    def update(self):
        # Keep looping indefinitely until the thread is stopped
        while True:
            # If the camera is stopped, stop the thread
            if self.stopped:
                # Close camera resources
                self.stream.release()
                return

            # Otherwise, grab the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
    # Return the most recent frame
        self.frame= cv2.resize(self.frame,(800,600))
        return self.frame

    def stop(self):
    # Indicate that the camera and thread should be stopped
        self.stopped = True


MODEL_NAME = 'TFLite_model'
GRAPH_NAME = 'detect.tflite'
LABELMAP_NAME = 'labelmap.txt'
min_conf_threshold = float(0.5)
resW, resH = '800x600'.split('x')
imW, imH = int(resW), int(resH)

def reconocimineto_stream(camara,fin,id_cam,id_tele):
    
    

    # Import TensorFlow libraries
    # If tflite_runtime is installed, import interpreter from tflite_runtime, else import from regular tensorflow
    # If using Coral Edge TPU, import the load_delegate library
    pkg = importlib.util.find_spec('tflite_runtime')
    if pkg:
        from tflite_runtime.interpreter import Interpreter
       
    else:
        from tensorflow.lite.python.interpreter import Interpreter
        

    
    # Get path to current working directory
    CWD_PATH = os.getcwd()

    # Path to .tflite file, which contains the model that is used for object detection
    PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,GRAPH_NAME)

    # Path to label map file
    PATH_TO_LABELS = os.path.join(CWD_PATH,MODEL_NAME,LABELMAP_NAME)

    # Load the label map
    with open(PATH_TO_LABELS, 'r') as f:
        labels = [line.strip() for line in f.readlines()]


    if labels[0] == '???':
        del(labels[0])

    # Load the Tensorflow Lite model.
    # If using Edge TPU, use special load_delegate argument
    interpreter = Interpreter(model_path=PATH_TO_CKPT)

    interpreter.allocate_tensors()

    # Get model details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    height = input_details[0]['shape'][1]
    width = input_details[0]['shape'][2]

    floating_model = (input_details[0]['dtype'] == np.float32)

    input_mean = 127.5
    input_std = 127.5

    # Initialize frame rate calculation
    frame_rate_calc = 1
    freq = cv2.getTickFrequency()

    # Initialize video stream
    videostream = VideoStream(resolution=(imW,imH),framerate=30,link=camara).start()
    time.sleep(1)

    auto=0
    persona=0
    correr= datetime.datetime.now()
    #corre_auto  = datetime.datetime.now()
    pathcarpeta='/home/pi/Documents/WebServer/Imagenes/'

    #for frame1 in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True):
    while True:
        hora_actual = datetime.datetime.now().minute
        ahora= datetime.datetime.now()
        if ahora>correr :
            
            # Start timer (for calculating frame rate)
            t1 = cv2.getTickCount()

            # Grab frame from video stream
            frame1 = videostream.read()

            # Acquire frame and resize to expected shape [1xHxWx3]
            frame = frame1.copy()
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (width, height))
            input_data = np.expand_dims(frame_resized, axis=0)

            # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
            if floating_model:
                input_data = (np.float32(input_data) - input_mean) / input_std

            # Perform the actual detection by running the model with the image as input
            interpreter.set_tensor(input_details[0]['index'],input_data)
            interpreter.invoke()

            # Retrieve detection results
            boxes = interpreter.get_tensor(output_details[0]['index'])[0] # Bounding box coordinates of detected objects
            classes = interpreter.get_tensor(output_details[1]['index'])[0] # Class index of detected objects
            scores = interpreter.get_tensor(output_details[2]['index'])[0] # Confidence of detected objects
            #num = interpreter.get_tensor(output_details[3]['index'])[0]  # Total number of detected objects (inaccurate and not needed)

            objetos=[]
            
            # Loop over all detections and draw detection box if confidence is above minimum threshold
            for i in range(len(scores)):
                if ((scores[i] > min_conf_threshold) and (scores[i] <= 1.0)):

                    # Get bounding box coordinates and draw box
                    # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
                    ymin = int(max(1,(boxes[i][0] * imH)))
                    xmin = int(max(1,(boxes[i][1] * imW)))
                    ymax = int(min(imH,(boxes[i][2] * imH)))
                    xmax = int(min(imW,(boxes[i][3] * imW)))
                    
                    cv2.rectangle(frame, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)

                    # Draw label
                    object_name = labels[int(classes[i])] # Look up object name from "labels" array using class index
                
                    label = '%s: %d%%' % (object_name, int(scores[i]*100)) # Example: 'person: 72%'
                    labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
                    label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
                    cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in
                    cv2.putText(frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text
                    time.sleep(1)

                    
                    if object_name=='persona':
                        persona=persona+1
                        objetos.append('Persona')
                                                        
                                    
                    if object_name=='auto':
                        auto=auto+1
                        objetos.append('Auto')
                        

                    if auto >10 or persona>10:
                        cv2.putText(frame,'Vi-SegurityIoT - ' + id_cam,(30,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2,cv2.LINE_AA)
                        #sumo 5 minutos a partir de ahora, una pausa digamos
                        correr = ahora + datetime.timedelta(0,0,0,0,1)
                        hora_actual= datetime.datetime.now().strftime("%d-%b-%Y-%H:%M:%S")
                        #guardo la imgen en la carpeta correspodiente a la camara
                        cv2.imwrite(pathcarpeta + id_cam + "/"+id_cam+'-'+ hora_actual +'.jpg',frame) 
                        Send_Telegram(pathcarpeta + id_cam + "/" +id_cam+'-'+ hora_actual +'.jpg',objetos,id_cam,id_tele)
                        time.sleep(1)

                        #guardo las novedades en el text
                        file1 = open("/home/pi/Documents/API-REST-Flask-ViSegurityIoT/text_eventos.txt","a")
                        file1.write('{ "evento": "' + id_cam + '" , "hora": "' + hora_actual + '" , "path": "' + pathcarpeta + id_cam + '/' +id_cam + '-' + hora_actual + '.jpg' + '" , "revisado": 0 }')
                        file1.write('\n')
                        file1.close()


        #Si la hora actual coincide con la final detengo el reconocimiento         
        if  hora_actual==fin:
            videostream.stop()
            break           



        
   

