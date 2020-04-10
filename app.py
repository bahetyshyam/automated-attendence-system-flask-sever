from flask import Flask, request, flash, redirect, jsonify
from werkzeug.utils import secure_filename
import os, pathlib
from face_scrapper.face_scrapper import extract_faces
import requests
import shutil

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

current_directory = pathlib.Path(__file__).parent.absolute()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return 'Home'

@app.route('/attendence', methods=['POST'])
def getAttendence():
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


if __name__ == '__main__':
    app.run(debug=True, port= 8080)
