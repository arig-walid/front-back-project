from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    app.logger.info('Upload endpoint hit')

    if 'image' not in request.files:
        app.logger.error('No image part in the request')
        return jsonify({'message': 'No image part in the request'}), 400

    file = request.files['image']
    if file.filename == '':
        app.logger.error('No selected file')
        return jsonify({'message': 'No selected file'}), 400

    x = request.form.get('x')
    y = request.form.get('y')

    if not x or not y:
        app.logger.error('Coordinates not provided')
        return jsonify({'message': 'Coordinates not provided'}), 400

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        app.logger.info(f'File saved to {file_path} at coordinates ({x}, {y})')
        return jsonify({'message': f'File uploaded successfully at coordinates ({x}, {y})'}), 200

@app.errorhandler(500)
def handle_500_error(_error):
    app.logger.error('Server error occurred')
    return jsonify({'message': 'Server error occurred'}), 500

if __name__ == '__main__':
    app.run(debug=True)
staticmethod