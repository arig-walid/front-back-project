from flask import Flask, request, jsonify, session
from PIL import Image, ExifTags
import numpy as np
import math

app = Flask(__name__)
app.secret_key = "hello"

@app.route('/update_base', methods=['POST'])
def base_update():
    global point, final_boxes, img
    image_file = request.files['image']
    base_coordinates = request.form['coordinates'].split(',')
    base_x, base_y = map(int, base_coordinates[0].split())
    web_width = int(request.form['width'])
    web_height = int(request.form['height'])

    pil_image = Image.open(image_file)
    orig_img = np.array(pil_image)

    # Check if the image has FOV metadata
    fov = None
    try:
        exif_data = pil_image._getexif()
        for tag, value in exif_data.items():
            tag_name = ExifTags.TAGS.get(tag, tag)
            if tag_name == "FocalLengthIn35mmFilm":
                fov = value
                break
    except Exception as e:
        print(f"Error retrieving FOV metadata: {e}")

    if fov:
        response_message = "Data sent successfully. Please click on the top point of the pole you want to measure."
    else:
        response_message = "Data sent successfully. Please click on the top of the measurement stick first."

    try:
        # Assuming detectWith_Yolov8 is a function to detect objects
        img, labels, boxes, ids, confs = detectWith_Yolov8(image_file, model)
        session['img'] = img
        session['labels'] = labels
        session['web_width'] = web_width
        session['web_height'] = web_height
        session['ids'] = ids
        session['confs'] = confs
        session['boxes'] = boxes

        return jsonify({"Base_point": response_message})
    except Exception as e:
        print(e, "Error...")
        return jsonify({"error": "Oops! We couldn't find/detect any poles in this image. Can you give it another shot with a different one OR try another one?"})

@app.route('/update_height', methods=['POST'])
def update_height():
    global point, final_boxes, img

    if 'img' not in session:
        return jsonify({"error": "No Image was found"})

    img = session['img']
    coordinates = request.form['coordinates'].split(',')
    original_x, original_y = map(int, coordinates[0].split())

    if 'stick_coordinates' in request.form:
        stick_coordinates = request.form['stick_coordinates'].split(',')
        stick_x, stick_y = map(int, stick_coordinates[0].split())
        img, height = calculate_height_with_stick(img, stick_x, stick_y, original_x, original_y)
    else:
        img, height = calculate_height(img, original_x, original_y)

    return jsonify({"height": height})

def calculate_height_with_stick(img, stick_x, stick_y, pole_x, pole_y):
    stick_height = 10  # Assume the stick height is known (e.g., 10 feet)
    stick_pixel_height = abs(stick_y - stick_x)
    pole_pixel_height = abs(pole_y - stick_y)
    pole_height = (pole_pixel_height / stick_pixel_height) * stick_height
    return img, pole_height

def calculate_height(img, pole_x, pole_y):
    fov = 90  # Assume a default FOV if not provided
    focal_length = 50  # Assume a default focal length if not provided
    pole_pixel_height = abs(pole_y - pole_x)
    pole_height = (pole_pixel_height / 1000) * (2 * math.tan(math.radians(fov / 2)) * focal_length)
    return img, pole_height

@app.route('/')
def index():
    return "Welcome to Pole Measurement Project!"

if __name__ == '__main__':
    app.run(debug=True)
