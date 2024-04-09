import os
from flask import Flask, request, render_template, send_file, send_from_directory
from csvhandling import process_csv
import zipfile
from werkzeug.utils import secure_filename
import shutil

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    # Serve index.html from the static folder
    return send_from_directory('static', 'index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file part'
    
    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        return 'No selected file'

    if not uploaded_file.filename.lower().endswith('.zip'):
        return 'Invalid file type. Please upload a zip file.'

    zip_filename = secure_filename(uploaded_file.filename)
    zip_path = os.path.join(app.config['UPLOAD_FOLDER'], zip_filename)
    uploaded_file.save(zip_path)

    # Extract files from the zip archive
    extract_zip_files(zip_path)

    # Process the extracted CSV file and template
    csv_file, template_file = find_csv_and_template()
    if not csv_file:
        return 'No CSV file found in the zip.'
    if not template_file:
        return 'No Markdown template file found in the zip.'

    output_zip_path = process_csv(csv_file, template_file)

    if not os.path.exists(output_zip_path):
        return 'Error processing CSV.'

    return send_file(output_zip_path, as_attachment=True)

def extract_zip_files(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file in zip_ref.namelist():
            zip_ref.extract(file, app.config['UPLOAD_FOLDER'])
    
    extracted_files = os.listdir(app.config['UPLOAD_FOLDER'])
    subfolder = next((f for f in extracted_files if os.path.isdir(os.path.join(app.config['UPLOAD_FOLDER'], f))), None)
    
    if subfolder:
        subfolder_path = os.path.join(app.config['UPLOAD_FOLDER'], subfolder)
        for item in os.listdir(subfolder_path):
            src = os.path.join(subfolder_path, item)
            dst = os.path.join(app.config['UPLOAD_FOLDER'], item)
            shutil.move(src, dst)
        os.rmdir(subfolder_path)

def find_csv_and_template():
    csv_file = None
    template_file = None
    for file in os.listdir(app.config['UPLOAD_FOLDER']):
        if file.lower().endswith('.csv'):
            csv_file = os.path.join(app.config['UPLOAD_FOLDER'], file)
        elif file.lower().endswith('.md'):
            template_file = os.path.join(app.config['UPLOAD_FOLDER'], file)
    return csv_file, template_file

if __name__ == '__main__':
    app.run(debug=True, port=8000)