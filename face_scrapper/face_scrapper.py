import cv2
import sys
import os
import pathlib

def extract_faces(imageFileName):
    currentDirectory = pathlib.Path(__file__).parent.absolute()
    parentDirectory = os.path.dirname(currentDirectory)
    imagePath = os.path.join(currentDirectory, imageFileName)


    image = cv2.imread(imagePath)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    faceCascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.3,
        minNeighbors=3,
        minSize=(30, 30)
    )

    print("[INFO] Found {0} Faces!".format(len(faces)))

    if not os.path.exists(os.path.join(parentDirectory,'detected_faces')):
        os.makedirs(os.path.join(parentDirectory,'detected_faces'))

    os.chdir(os.path.join(parentDirectory,'detected_faces'))

    i = 1
    for (x, y, w, h) in faces:
        roi_color = image[y:y + h, x:x + w] 
        print("[INFO] Object found. Saving locally.")
        cv2.imwrite(str(i) + '_faces.jpg', roi_color)# for storing each individual face detected
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)# for drawing a rectangle around each individual face
        i += 1  


    os.chdir(currentDirectory)

    status = cv2.imwrite('faces_detected.jpg', image)
    print("[INFO] Image faces_detected.jpg written to filesystem: ", status)
