from flask import Flask, request, flash, redirect, jsonify
from werkzeug.utils import secure_filename
import os
import pathlib
from datetime import datetime
import requests
import shutil
import face_recognition
import numpy as np
from dotenv import load_dotenv

# mongo db
import pymongo
from pymongo import MongoClient
from bson import ObjectId

# custom functions and variables
from face_scrapper.face_scrapper import extract_faces
from face_encodings import known_faces_encodings


#mongo db initialization
load_dotenv('.env')
client = MongoClient(os.getenv('MONGO_URI'))
db = client['automated-attendance']
students_collection = db.students
attendance_collection = db.attendance

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

current_directory = pathlib.Path(__file__).parent.absolute()

known_faces_usn = [
    '1js16is001',
    '1js16is002',
    '1js16is003',
    '1js16is004',
    '1js16is005',
    '1js16is006',
    '1js16is007',
    '1js16is008',
    '1js16is009',
    '1js16is010',
]


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return 'Home'

#send an image with image as the key value in multipart/formdata format and send the subject and the classname as url parameters
@app.route('/face-detection/<subject>/<classname>', methods=['POST'])
def faceDetection(subject, classname):
    #to remove the enhanced and detected faces directory
    detected_faces_directory = os.path.join(current_directory, 'detected_faces')
    enhanced_faces_directory = os.path.join(current_directory, 'enhanced_faces')

    if os.path.exists(detected_faces_directory):
        shutil.rmtree(detected_faces_directory)
    if os.path.exists(enhanced_faces_directory):
        shutil.rmtree(enhanced_faces_directory)

    print(subject)
    print(classname)
    # check if the key value pair of the image sent is correct or not
    if 'image' not in request.files:
        return jsonify({
            "success": False,
            "message": '''Key name of file sent should be "image" '''
        }), 400
    file = request.files['image']

    # check if a file is selected or not
    if file.filename == '':
        return jsonify({
            "success": False,
            "message": "No file selected"
        }), 400

    # check if file is one of those extensions
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(current_directory, 'face_scrapper', filename))
        extract_faces(filename)  # perform face detection using opencv

        url = 'http://max-image-resolution-enhancer.codait-prod-41208c73af8fca213512856c7a09db52-0000.us-east.containers.appdomain.cloud/model/predict'
        # url = 'http://localhost:5000/model/predict'
        detected_faces_directory = os.path.join(
            current_directory, 'detected_faces')
        enhanced_faces_directory = os.path.join(
            current_directory, 'enhanced_faces')

        # check if enhanced_faced directory exists, if not, create the direcroty
        if not os.path.exists(enhanced_faces_directory):
            os.makedirs(enhanced_faces_directory)

        # loop through the images in detected_faces directory
        for detected_filename in os.listdir(detected_faces_directory):
            os.chdir(detected_faces_directory)
            files = {'image': open(detected_filename, 'rb')}
            # making a request to the image enhancer
            r = requests.post(url, files=files, stream=True)
            os.chdir(enhanced_faces_directory)
            if r.status_code == 200:
                with open('enhanced_'+detected_filename, 'wb') as f:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)

        #recognition below this
        present_usn_list = []
        os.chdir(current_directory)

        for image_file in os.listdir("enhanced_faces"):

            # load the new unknown image
            unknown_image = face_recognition.load_image_file(
                "./enhanced_faces/"+image_file)

            # generate face encoding of unknown image
            try:
                unknown_face_encoding = face_recognition.face_encodings(unknown_image)[
                    0]
            except IndexError:
                continue

            face_distance_results = face_recognition.face_distance(
                known_faces_encodings, unknown_face_encoding)

            min_distance = 1
            min_index = -1
            for i in range(len(face_distance_results)):
                if face_distance_results[i] > .53:
                    continue
                if face_distance_results[i] < min_distance:
                    min_distance = face_distance_results[i]
                    min_index = i

            print(min_distance)

            if min_index != -1 and known_faces_usn[min_index] not in present_usn_list:
                present_usn_list.append(known_faces_usn[min_index])

        present_usn_list.sort()
        absent_usn_list = list(set(known_faces_usn) - set(present_usn_list))
        absent_usn_list.sort()

        # attendance_data = request.get_json()
        # subject = attendance_data['subject']
        # classname = attendance_data['class']

        try:
            savedAttendance = attendance_collection.insert_one(
                {
                    "date": datetime.utcnow(),
                    "subject": subject,
                    "class": classname,
                    "present": present_usn_list,
                    "absent": absent_usn_list
                }
            )

            result = attendance_collection.find_one(
                {"_id": savedAttendance.inserted_id})
            result.pop('_id')

        except pymongo.errors.PyMongoError:
            return jsonify({
                "success" : False,
                "message" : "Internal Server Error"
            }), 500

        return jsonify({
            "success" : True,
            "result": result
        })

    else:
        return jsonify({
            "success": False,
            "message": "Upload png, jpg, or jpeg image only"
        }), 400


#GET request to get details of all the students
@app.route('/students', methods=['GET'])
def getAllStudents():
    students = []
    try:
        x = students_collection.find()
        for item in x:
            item['_id'] = str(item['_id'])
            students.append(item)
        return jsonify({
            "success" : True,
            "students" : students
        })
    except pymongo.errors.PyMongoError:
        return jsonify({
            "success" : False,
            "message" : "Internal Server Error"
        }), 500


#GET request to get the attendance of all instances of attendance
@app.route('/attendance', methods=['GET'])
def getAllAttendance():
    attendance = []
    try: 
        x = attendance_collection.find()
        for item in x:
            item['_id'] = str(item['_id'])
            attendance.append(item)
        return jsonify({
            "attendance": attendance
        })
    except pymongo.errors.PyMongoError:
        return jsonify({
            "success" : False,
            "message" : "Internal Server Error"
        }), 500


if __name__ == '__main__':
    app.run(debug=True, port=8080)
