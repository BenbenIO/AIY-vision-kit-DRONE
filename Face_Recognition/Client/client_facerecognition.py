#!/usr/bin/env python3
from picamera import PiCamera
from time import sleep

from aiy.vision.inference import CameraInference
from aiy.vision.models import face_detection

import pickle
from PIL import Image 
import io
import socket

HOST = '192.168.1.104'   # The server's hostname or IP address
PORT = 6666              # The port used by the server

def sendMessage(conn, message):
    conn.sendall(message.encode('UTF-8'))
    

def waitack(conn, acktype):
    ack = conn.recv(1024).decode('UTF-8')    
    while ack != acktype:
         ack = conn.recv(1024).decode('UTF-8')
         
def sendImage(conn, image):
    conn.sendall(image)
    
def waitOverwrite(conn):
    overwrite = conn.recv(1024).decode('UTF-8')
    while overwrite != "OVERWRITE":
        overwrite = conn.recv(1024).decode('UTF-8')

def main():
    # Counting server call
    scall=0
    
    print("Binding with serve...")
    # Open socket:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conn:
        conn.connect((HOST, PORT))
        print("Connected to server")
        print("PiCamera initialization...")
        with PiCamera(sensor_mode=4, resolution=(1640, 1232), framerate=30) as camera:
            print("Camera inference - model loading...")
            print("Waiting for overwrite order...")
            waitOverwrite(conn)
            
            with CameraInference(face_detection.model()) as inference:
                print("Running the inference...")
                #sleep(1)
                #Get the RC-overwrite channel
            
                for result in inference.run():
                    faces = face_detection.get_faces(result)
                    print('num_faces= %d' %(len(faces)))
                
                    if(len(faces)>0):
                        # Start a stream to get the frame to crop // maybe a betterway hidden in the inference?
                        stream = io.BytesIO()
                        camera.capture(stream, format='jpeg')
                        stream.seek(0)
                        image = Image.open(stream)
                        image.save("full.jpg")
                        #print("Got stream shot")
                    
                        # Get the number of detected face:
                        nb_face = len(faces)
                    
                        # Get bounding box:
                        x, y, width, height = faces[0].bounding_box
                    
                        # Crop the image:
                        croppedface = image.crop((x,y, x+width,y+height))
                        #print("Image cropped")
                        #croppedface.save('face.jpg')
                    
                        # Get the byte array of the image without saving on the disk:
                        imgByteArr = io.BytesIO()
                        croppedface.save(imgByteArr, format='jpeg')
                        imgByteArr = imgByteArr.getvalue()
                        #print("Binary convertion")
                    
                        # Get size of binary array:
                        bin_size = len(imgByteArr)
                        h, w = croppedface.size

                        # Send the number of detected face:
                        message_nbface = "NBFACES " + str(nb_face)
                        sendMessage(conn, message_nbface)
                        waitack(conn, "NBFACE_ACK")
                        print("NBFACE_ACK recieved")
                        
                        for i in range(0, nb_face):
                            # Send image size:
                            message_imgsize = "SIZE " +str(int(bin_size))
                            sendMessage(conn, message_imgsize)
                            waitack(conn, "SIZE_ACK")
                            print("SIZE_ACK recieved")
                        
                            # Send the image
                            sendImage(conn, imgByteArr)
                            waitack(conn, "IMG_ACK")
                            print("IMG_ACK recieved")
                            
                        scall = scall+1
                        if(scall>5):
                           conn.close()
                           break            
                            

if __name__ == '__main__':
    main()