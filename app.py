from flask import Flask, request, flash, redirect, jsonify
from werkzeug.utils import secure_filename
import os, pathlib
from face_scrapper.face_scrapper import extract_faces
import requests
import shutil
import face_recognition

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

current_directory = pathlib.Path(__file__).parent.absolute()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return 'Home'

@app.route('/face-detection', methods=['POST'])
def faceDetection():
    #check if the key value pair of the image sent is correct or not
    if 'image' not in request.files:
        return jsonify({'message': '''Key name of file sent should be "image" '''})
    file = request.files['image']

    #check if a file is selected or not
    if file.filename == '':
        return 'No selected file'

    #check if file is one of those extensions
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(current_directory, 'face_scrapper', filename))
        extract_faces(filename) #perform face detection using opencv

        url = 'http://max-image-resolution-enhancer.max.us-south.containers.appdomain.cloud/model/predict'
        # url = 'http://localhost:5000/model/predict'
        detected_faces_directory = os.path.join(current_directory,'detected_faces')
        enhanced_faces_directory = os.path.join(current_directory,'enhanced_faces')

        #check if enhanced_faced directory exists, if not, create the direcroty
        if not os.path.exists(enhanced_faces_directory):
            os.makedirs(enhanced_faces_directory)

        #loop through the images in detected_faces directory
        for detected_filename in os.listdir(detected_faces_directory):
            os.chdir(detected_faces_directory)
            files = {'image' : open(detected_filename, 'rb')}
            r = requests.post(url, files=files, stream= True) #making a request to the image enhancer
            os.chdir(enhanced_faces_directory)
            if r.status_code == 200:
                with open('enhanced_'+detected_filename, 'wb') as f:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)
        return 'saved and enhanced'
    else:
        return "Upload png, jpg, or jpeg image only"

@app.route('/face-recognition', methods=['POST'])
def faceRecognition():
    if 'image' not in request.files:
        return jsonify({'message': '''Key name of file sent should be "image" '''})
    file = request.files['image']

    #check if a file is selected or not
    if file.filename == '':
        return 'No selected file'

    #train the model with single faces
    abhin_image = face_recognition.load_image_file("./training_set/abhin.jpg")
    gs_image = face_recognition.load_image_file("./training_set/gs.jpg")
    kishan_image = face_recognition.load_image_file("./training_set/kishan.jpg")
    monisha_image = face_recognition.load_image_file("./training_set/monisha.jpg")
    naik_image = face_recognition.load_image_file("./training_set/naik.jpg")
    prathik_image = face_recognition.load_image_file("./training_set/prathik.jpg")
    rachana_image = face_recognition.load_image_file("./training_set/rachana.jpg")
    sharad_image = face_recognition.load_image_file("./training_set/sharad.jpg")
    shyam_image = face_recognition.load_image_file("./training_set/shyam.jpg")
    vishwa_image = face_recognition.load_image_file("./training_set/vishwa.jpg")
    #load the new unknown posted image
    unknown_image = face_recognition.load_image_file(file)

    try:
        #create face encodings for each face and for new unknown posted image
        abhin_face_encoding = face_recognition.face_encodings(abhin_image)[0]
        gs_face_encoding = face_recognition.face_encodings(gs_image)[0]
        kishan_face_encoding = face_recognition.face_encodings(kishan_image)[0]
        monisha_face_encoding = face_recognition.face_encodings(monisha_image)[0]
        naik_face_encoding = face_recognition.face_encodings(naik_image)[0]
        prathik_face_encoding = face_recognition.face_encodings(prathik_image)[0]
        rachana_face_encoding = face_recognition.face_encodings(rachana_image)[0]
        sharad_face_encoding = face_recognition.face_encodings(sharad_image)[0]
        shyam_face_encoding = face_recognition.face_encodings(shyam_image)[0]
        vishwa_face_encoding = face_recognition.face_encodings(vishwa_image)[0]
        unknown_face_encoding = face_recognition.face_encodings(unknown_image)[0]
    except IndexError:
        print("I wasn't able to locate any faces in at least one of the images. Check the image files. Aborting...")
        quit()

    known_faces = [
        abhin_face_encoding,
        gs_face_encoding,
        kishan_face_encoding,
        monisha_face_encoding,
        naik_face_encoding,
        prathik_face_encoding,
        rachana_face_encoding,
        sharad_face_encoding,
        shyam_face_encoding,
        vishwa_face_encoding
    ]

    results = face_recognition.compare_faces(known_faces, unknown_face_encoding)

    for i in range(len(results)):
        if results[i] == True:
            #return index of person recognized
            return str(i)
    #else return -1
    return '-1'

if __name__ == '__main__':
    app.run(debug=True, port= 8080)
