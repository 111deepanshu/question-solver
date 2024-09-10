import os
import fitz  # PyMuPDF
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['OUTPUT_FOLDER'] = 'static/output/'
ALLOWED_EXTENSIONS = {'pdf'}

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def pdf_to_images(filepath, output_folder):
    doc = fitz.open(filepath)
    images = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        output_image = f"page_{page_num + 1}.png"
        output_path = os.path.join(output_folder, output_image)
        pix.save(output_path)
        images.append(output_image)
    return images

@app.route('/')
def upload_file():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        images = pdf_to_images(filepath, app.config['OUTPUT_FOLDER'])
        return jsonify({"images": images}), 200
    
    return jsonify({"error": "Invalid file type"}), 400

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    completed_questions = data.get('questions', [])
    question_times = data.get('times', {})
    # Process the data as needed
    return jsonify({"message": f"You completed {len(completed_questions)} questions!"})

if __name__ == '__main__':
    app.run(debug=True)
