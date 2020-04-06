from flask import Flask, request, flash, redirect, jsonify
from werkzeug.utils import secure_filename
import os, pathlib
from face_scrapper.face_scrapper import extract_faces


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return 'Home'


@app.route('/attendence', methods=['POST'])
def getAttendence():
    if 'image' not in request.files:
        # print('No file found')
        return jsonify({'message': '''Key name of file sent should be "image" '''})
    file = request.files['image']

    if file.filename == '':
        return 'No selected file'

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(pathlib.Path(__file__).parent.absolute(), 'face_scrapper', filename))
        extract_faces(filename)
        return 'saved'
    else:
        return "Upload png, jpg, or jpeg image only"


if __name__ == '__main__':
    app.run(debug=True)
