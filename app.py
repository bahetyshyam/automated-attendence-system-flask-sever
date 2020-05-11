from flask import Flask, request, flash, redirect, jsonify
from werkzeug.utils import secure_filename
import os, pathlib
from datetime import datetime
import requests
import shutil
import face_recognition
import numpy as np

#mongo db
import pymongo
from pymongo import MongoClient
from bson import ObjectId

#custom functions and variables
from face_scrapper.face_scrapper import extract_faces
from face_encodings import known_faces_encodings


client = MongoClient("mongodburi")
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

        url = 'http://max-image-resolution-enhancer.codait-prod-41208c73af8fca213512856c7a09db52-0000.us-east.containers.appdomain.cloud/model/predict'
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
        
        #train the model with single faces
        # abhin_image = face_recognition.load_image_file("./training_set/abhin.jpg")
        # gs_image = face_recognition.load_image_file("./training_set/gs.jpg")
        # kishan_image = face_recognition.load_image_file("./training_set/kishan.jpg")
        # monisha_image = face_recognition.load_image_file("./training_set/monisha.jpg")
        # naik_image = face_recognition.load_image_file("./training_set/naik.jpg")
        # prathik_image = face_recognition.load_image_file("./training_set/prathik.jpg")
        # rachana_image = face_recognition.load_image_file("./training_set/rachana.jpg")
        # sharad_image = face_recognition.load_image_file("./training_set/sharad.jpg")
        # shyam_image = face_recognition.load_image_file("./training_set/shyam.jpg")
        # vishwa_image = face_recognition.load_image_file("./training_set/vishwa.jpg")

        # try:
            #create face encodings for each face and for new unknown posted image
            # abhin_face_encoding = face_recognition.face_encodings(abhin_image)[0]
            # gs_face_encoding = face_recognition.face_encodings(gs_image)[0]
            # kishan_face_encoding = face_recognition.face_encodings(kishan_image)[0]
            # monisha_face_encoding = face_recognition.face_encodings(monisha_image)[0]
            # naik_face_encoding = face_recognition.face_encodings(naik_image)[0]
            # prathik_face_encoding = face_recognition.face_encodings(prathik_image)[0]
            # rachana_face_encoding = face_recognition.face_encodings(rachana_image)[0]
            # sharad_face_encoding = face_recognition.face_encodings(sharad_image)[0]
            # shyam_face_encoding = face_recognition.face_encodings(shyam_image)[0]
            # vishwa_face_encoding = face_recognition.face_encodings(vishwa_image)[0]
        # except IndexError:
        #     print("I wasn't able to locate any faces in the image. Check the image file. Aborting...")
        #     quit()

        # known_faces_encodings = [
        #     abhin_face_encoding,
        #     gs_face_encoding,
        #     kishan_face_encoding,
        #     monisha_face_encoding,
        #     naik_face_encoding,
        #     prathik_face_encoding,
        #     rachana_face_encoding,
        #     sharad_face_encoding,
        #     shyam_face_encoding,
        #     vishwa_face_encoding
        # ]
    #     os.chdir(current_directory)

    #     present_usn_list = []

    #     for image_file in os.listdir("enhanced_faces"):

    #         #load the new unknown image
    #         unknown_image = face_recognition.load_image_file("./enhanced_faces/"+image_file)

    #         #generate face encoding of unknown image
    #         try:
    #             unknown_face_encoding = face_recognition.face_encodings(unknown_image)[0]
    #         except IndexError:
    #             continue

    #         face_distance_results = face_recognition.face_distance(known_faces_encodings, unknown_face_encoding)

    #         min_distance = 1
    #         min_index = -1
    #         for i in range(len(face_distance_results)):
    #             if face_distance_results[i] > .53:
    #                 continue
    #             if face_distance_results[i] < min_distance:
    #                 min_distance = face_distance_results[i]
    #                 min_index = i

    #         print(min_distance)

    #         if min_index != -1 and known_faces_usn[min_index] not in present_usn_list:
    #             present_usn_list.append(known_faces_usn[min_index])
            
        
    #     present_usn_list.sort()    
    #     absent_usn_list = list(set(known_faces_usn) - set(present_usn_list))
    #     absent_usn_list.sort()

    #     attendance_data = request.get_json()
    #     subject = attendance_data['subject']
    #     classname = attendance_data['class']

    #     savedAttendance = attendance_collection.insert_one(
    #         {
    #             "date" : datetime.utcnow(),
    #             "subject" : subject,
    #             "class" : classname,
    #             "present" : present_usn_list,
    #             "absent" : absent_usn_list
    #         }
    #     )
    
    #     finalresult = attendance_collection.find_one({"_id" : savedAttendance.inserted_id})
    #     finalresult.pop('_id')

    #     print(finalresult)

    #     return jsonify({
    #         "result" : finalresult
    #     })

        
    # else:
    #     return "Upload png, jpg, or jpeg image only"

@app.route('/face-recognition', methods=['POST'])
def faceRecognition():

    #train the model with single faces
    # abhin_image = face_recognition.load_image_file("./training_set/abhin.jpg")
    # gs_image = face_recognition.load_image_file("./training_set/gs.jpg")
    # kishan_image = face_recognition.load_image_file("./training_set/kishan.jpg")
    # monisha_image = face_recognition.load_image_file("./training_set/monisha.jpg")
    # naik_image = face_recognition.load_image_file("./training_set/naik.jpg")
    # prathik_image = face_recognition.load_image_file("./training_set/prathik.jpg")
    # rachana_image = face_recognition.load_image_file("./training_set/rachana.jpg")
    # sharad_image = face_recognition.load_image_file("./training_set/sharad.jpg")
    # shyam_image = face_recognition.load_image_file("./training_set/shyam.jpg")
    # vishwa_image = face_recognition.load_image_file("./training_set/vishwa.jpg")

    # try:
        #create face encodings for each face and for new unknown posted image
        # abhin_face_encoding = face_recognition.face_encodings(abhin_image)[0]
        # gs_face_encoding = face_recognition.face_encodings(gs_image)[0]
        # kishan_face_encoding = face_recognition.face_encodings(kishan_image)[0]
        # monisha_face_encoding = face_recognition.face_encodings(monisha_image)[0]
        # naik_face_encoding = face_recognition.face_encodings(naik_image)[0]
        # prathik_face_encoding = face_recognition.face_encodings(prathik_image)[0]
        # rachana_face_encoding = face_recognition.face_encodings(rachana_image)[0]
        # sharad_face_encoding = face_recognition.face_encodings(sharad_image)[0]
        # shyam_face_encoding = face_recognition.face_encodings(shyam_image)[0]
        # vishwa_face_encoding = face_recognition.face_encodings(vishwa_image)[0]
    # except IndexError:
    #     print("I wasn't able to locate any faces in the image. Check the image file. Aborting...")
    #     quit()

    # known_faces_encodings = [
    #     abhin_face_encoding,
    #     gs_face_encoding,
    #     kishan_face_encoding,
    #     monisha_face_encoding,
    #     naik_face_encoding,
    #     prathik_face_encoding,
    #     rachana_face_encoding,
    #     sharad_face_encoding,
    #     shyam_face_encoding,
    #     vishwa_face_encoding
    # ]

    present_usn_list = []

    for image_file in os.listdir("enhanced_faces"):

        #load the new unknown image
        unknown_image = face_recognition.load_image_file("./enhanced_faces/"+image_file)

        #generate face encoding of unknown image
        try:
            unknown_face_encoding = face_recognition.face_encodings(unknown_image)[0]
        except IndexError:
            continue

        face_distance_results = face_recognition.face_distance(known_faces_encodings, unknown_face_encoding)

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

    attendance_data = request.get_json()
    subject = attendance_data['subject']
    classname = attendance_data['class']

    result = attendance_collection.insert_one(
        {
            "date" : datetime.utcnow(),
            "subject" : subject,
            "class" : classname,
            "present" : present_usn_list,
            "absent" : absent_usn_list
        }
    )

    # print(result.inserted_id)
    # print(type(result.inserted_id))
 

    finalresult = attendance_collection.find_one({"_id" : result.inserted_id})
    finalresult.pop('_id')

    print(finalresult)

    return jsonify({
        "result" : finalresult
    })



@app.route('/students', methods=['GET'])
def getAllStudents():
    students = [] 
    try: 
        x = students_collection.find()
        for item in x:
            item['_id'] = str(item['_id'])
            students.append(item)
        return jsonify({"students" : students})
    except pymongo.errors.PyMongoError:
        return jsonify({"error" : "an error occured"})
    


if __name__ == '__main__':
    app.run(debug=True, port= 8080)
