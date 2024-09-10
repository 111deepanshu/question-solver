import os
import fitz  # PyMuPDF
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)

# Configuration for file uploads
UPLOAD_FOLDER = 'uploads/'
OUTPUT_FOLDER = 'static/output/'  # Store output images
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Create the necessary directories if they don't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

# Function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to convert PDF to images
def pdf_to_images(filepath, output_folder):
    doc = fitz.open(filepath)  # Open the uploaded PDF
    images = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)  # Get each page
        pix = page.get_pixmap()  # Convert page to an image
        output_image = os.path.join(output_folder, f"page_{page_num + 1}.png")
        pix.save(output_image)
        images.append(output_image)  # Append the path of the image for reference
    return images


# Route for file upload page
@app.route('/')
def upload_file():
    return render_template('upload.html')

# Route to handle file uploads
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file part"
    
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Convert the PDF to images
        images = pdf_to_images(filepath, app.config['OUTPUT_FOLDER'])

        return render_template('display_images.html', images=images)
    
    return "Invalid file type"

@app.route('/submit', methods=['POST'])
def submit():
    completed_questions = request.form.getlist('questions')
    # Do something with the completed questions, like store them in a database
    return f'You completed {len(completed_questions)} questions!'

if __name__ == '__main__':
    app.run(debug=True)