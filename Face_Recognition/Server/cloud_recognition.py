#!/usr/bin/env python3
import cv2
import os
import numpy as np

import socket
import pickle
import cv2
from PIL import Image

HOST = '192.168.1.187'  
PORT = 6666     

subjects = ["", "Mario", "Arnaud", "Benjamin"]

# Socket related function:
def waitNBFACE(conn):
    data = conn.recv(1024).decode('UTF-8')
    
    while not data.startswith("NBFACES"):
        data = conn.recv(1024).decode('UTF-8')
    
    nb_face = data.split()[1]    
    return nb_face
    
def waitIMGSIZE(conn):
    data = conn.recv(1024).decode('UTF-8')
    
    while not data.startswith("SIZE"):
        data = conn.recv(1024).decode('UTF-8')
    
    img_size = data.split()[1]    
    return img_size
    
def recievedIMG(conn, img_size):
    image = b""
    
    while len(image) < img_size:
       tmp = conn.recv(4096)
       if tmp:
           image += tmp
    
    return image

def sendack(conn, acktype):
    conn.sendall(acktype.encode('UTF-8'))
    
# Recognition related function:
def convert_grey(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return gray

def draw_text(img, text, x, y):
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)

def predict(face_recognizer, test_img):
    img = test_img.copy()
    if not img is None:
        greyface = convert_grey(img)

        label, confidence = face_recognizer.predict(greyface)
        label_text = subjects[label]
        print("Cloud recognized: " + label_text)
    
        draw_text(img, label_text, 50, 50)
    return img
    
    
def main():
    
    print("Loading trained facerecognition model...")
    face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    face_recognizer.read("opencv-files/lbph_addedPiCAM.yml")
    print("Socket initialization")
    # Counting server call
    scall=0
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOST, PORT))
        sock.listen()
        while True:
            print("Waiting drone binding...")
            conn, addr = sock.accept()
            with conn:
                # Waiting for user to send the command Overwrite
                print("Drone-server binding done")
                feu = input("Press enter to send the Overwrite command")
                sendack(conn, "OVERWRITE")
                print("Ready, send me pretty face")
                    
                while True:
                    # Get number of detected face:
                    nb_face = int(waitNBFACE(conn))
                    print("NB_FACE :" + str(nb_face))
                    sendack(conn, "NBFACE_ACK")
                    
                    for i in range(0, nb_face):
                        # Get size of the face_image
                        img_size = int(waitIMGSIZE(conn))
                        print("IMG_SIZE : " + str(img_size))
                        sendack(conn, "SIZE_ACK")
                    
                        # Recieved the face_img
                        image_data = recievedIMG(conn, img_size)
                        sendack(conn, "IMG_ACK")
                        print("IMG recieved")
                    
                        # Saved the image:
                        with open("raw.jpg", 'wb') as img:
                           img.write(image_data)
                        
                        # Convert to cv image or open the saved pic
                        #image_face = Image.frombytes('RGBA', (128,128), image_data, 'raw')
                        #open_cv_image = np.array(image_face)
                        #cvface = open_cv_image[:, :, ::-1].copy() 
                        cvface = cv2.imread("raw.jpg")
                        grey = convert_grey(cvface)
                        predicted = predict(face_recognizer, grey)
                        cv2.imwrite('saved_predicted/predicted_'+str(scall)+'_'+str(i)+'.png', predicted)
                        #cv2.imshow(subjects[3], cv2.resize(predicted, (400, 500)))
                        #cv2.waitKey(0)
                        #cv2.destroyAllWindows()
                    scall=scall+1          
                    #break
                   
                
if __name__ == '__main__':
    main()
