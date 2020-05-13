# # send the values in the format below in application/json
# # {
# #     "subject" : "ADA",
# #     "class" : "8 A"
# # }
# @app.route('/face-recognition', methods=['POST'])
# def faceRecognition():

#     # train the model with single faces
#     # abhin_image = face_recognition.load_image_file("./training_set/abhin.jpg")
#     # gs_image = face_recognition.load_image_file("./training_set/gs.jpg")
#     # kishan_image = face_recognition.load_image_file("./training_set/kishan.jpg")
#     # monisha_image = face_recognition.load_image_file("./training_set/monisha.jpg")
#     # naik_image = face_recognition.load_image_file("./training_set/naik.jpg")
#     # prathik_image = face_recognition.load_image_file("./training_set/prathik.jpg")
#     # rachana_image = face_recognition.load_image_file("./training_set/rachana.jpg")
#     # sharad_image = face_recognition.load_image_file("./training_set/sharad.jpg")
#     # shyam_image = face_recognition.load_image_file("./training_set/shyam.jpg")
#     # vishwa_image = face_recognition.load_image_file("./training_set/vishwa.jpg")

#     # try:
#     # create face encodings for each face and for new unknown posted image
#     # abhin_face_encoding = face_recognition.face_encodings(abhin_image)[0]
#     # gs_face_encoding = face_recognition.face_encodings(gs_image)[0]
#     # kishan_face_encoding = face_recognition.face_encodings(kishan_image)[0]
#     # monisha_face_encoding = face_recognition.face_encodings(monisha_image)[0]
#     # naik_face_encoding = face_recognition.face_encodings(naik_image)[0]
#     # prathik_face_encoding = face_recognition.face_encodings(prathik_image)[0]
#     # rachana_face_encoding = face_recognition.face_encodings(rachana_image)[0]
#     # sharad_face_encoding = face_recognition.face_encodings(sharad_image)[0]
#     # shyam_face_encoding = face_recognition.face_encodings(shyam_image)[0]
#     # vishwa_face_encoding = face_recognition.face_encodings(vishwa_image)[0]
#     # except IndexError:
#     #     print("I wasn't able to locate any faces in the image. Check the image file. Aborting...")
#     #     quit()

#     # known_faces_encodings = [
#     #     abhin_face_encoding,
#     #     gs_face_encoding,
#     #     kishan_face_encoding,
#     #     monisha_face_encoding,
#     #     naik_face_encoding,
#     #     prathik_face_encoding,
#     #     rachana_face_encoding,
#     #     sharad_face_encoding,
#     #     shyam_face_encoding,
#     #     vishwa_face_encoding
#     # ]

#     present_usn_list = []
#     os.chdir(current_directory)

#     for image_file in os.listdir("enhanced_faces"):

#         # load the new unknown image
#         unknown_image = face_recognition.load_image_file(
#             "./enhanced_faces/"+image_file)

#         # generate face encoding of unknown image
#         try:
#             unknown_face_encoding = face_recognition.face_encodings(unknown_image)[
#                 0]
#         except IndexError:
#             continue

#         face_distance_results = face_recognition.face_distance(
#             known_faces_encodings, unknown_face_encoding)

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

#     try:
#         savedAttendance = attendance_collection.insert_one(
#             {
#                 "date": datetime.utcnow(),
#                 "subject": subject,
#                 "class": classname,
#                 "present": present_usn_list,
#                 "absent": absent_usn_list
#             }
#         )

#         result = attendance_collection.find_one(
#             {"_id": savedAttendance.inserted_id})
#         result.pop('_id')

#     except pymongo.errors.PyMongoError:
#         return jsonify({
#             "success": False,
#             "message": "Internal Server Error"
#         }), 500

#     # to remove the enhanced and detected faces directory
#     detected_faces_directory = os.path.join(
#         current_directory, 'detected_faces')
#     enhanced_faces_directory = os.path.join(
#         current_directory, 'enhanced_faces')

#     if os.path.exists(detected_faces_directory):
#         shutil.rmtree(detected_faces_directory)
#     if os.path.exists(enhanced_faces_directory):
#         shutil.rmtree(enhanced_faces_directory)

#     return jsonify({
#         "success": True,
#         "result": result
#     })
