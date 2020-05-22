#classification part starts here
def classify(file):
    classes=['abhin', 'gs', 'kishan', 'monisha', 'naik', 'prathik', 'rachana', 'sharad', 'shyam', 'vishwa']

    model_filepath = 'attendance_v12.h5'

    model = tensorflow.keras.models.load_model(
        model_filepath,
        custom_objects=None,
        compile=False
    )

    from keras.preprocessing import image
    test_image = image.load_img(file, target_size=(128, 128))
    test_image = image.img_to_array(test_image)
    test_image = np.expand_dims(test_image, axis=0)
    result = model.predict(test_image)

    result = np.array(result)

    return classes[np.argmax(result)]