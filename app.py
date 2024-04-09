#import the nesesary modules
import os
from flask import Flask, request, send_file, send_from_directory
from csvhandling import process_csv
import zipfile
from werkzeug.utils import secure_filename
import shutil

app = Flask(__name__)

# Define the upload folder for storing uploaded ZIP files
UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Define the output folder for storing processed files
OUTPUT_FOLDER = os.path.join(app.root_path, 'output')
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    # Serve index.html from the static folder
    return send_from_directory('static', 'index.html')

@app.route('/upload', methods=['POST'])
def upload():
    # Check if 'file' is present in the request
    if 'file' not in request.files:
        return 'No file part'

    # Retrieve the uploaded file from the request
    uploaded_file = request.files['file']
    # Check if a file is selected
    if uploaded_file.filename == '':
        return 'No selected file'

    # Check if the uploaded file has a .zip extension
    if not uploaded_file.filename.lower().endswith('.zip'):
        return 'Invalid file type. Please upload a zip file.'

    # Securely save the uploaded zip file to the upload folder
    zip_filename = secure_filename(uploaded_file.filename)
    zip_path = os.path.join(app.config['UPLOAD_FOLDER'], zip_filename)
    uploaded_file.save(zip_path)

    # Extract files from the uploaded zip archive
    extract_zip_files(zip_path)

    # Find the extracted CSV file and Markdown template
    csv_file, template_file = find_csv_and_template()
    if not csv_file:
        return 'No CSV file found in the zip.'
    if not template_file:
        return 'No Markdown template file found in the zip.'

    # Process the extracted CSV file and template
    output_zip_path = process_csv(csv_file, template_file)

    # Check if the processing was successful
    if not os.path.exists(output_zip_path):
        return 'Error processing CSV.'

    # Send the processed ZIP file as an attachment
    return send_file(output_zip_path, as_attachment=True)

def extract_zip_files(zip_path):
    # Extract files from the zip archive to the upload folder
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(app.config['UPLOAD_FOLDER'])

    # Find any subfolder within the upload folder
    extracted_files = os.listdir(app.config['UPLOAD_FOLDER'])
    subfolder = next((f for f in extracted_files if os.path.isdir(os.path.join(app.config['UPLOAD_FOLDER'], f))), None)

    # If a subfolder is found, move its contents to the upload folder
    if subfolder:
        subfolder_path = os.path.join(app.config['UPLOAD_FOLDER'], subfolder)
        for item in os.listdir(subfolder_path):
            src = os.path.join(subfolder_path, item)
            dst = os.path.join(app.config['UPLOAD_FOLDER'], item)
            shutil.move(src, dst)
        # Remove the subfolder once its contents are moved
        os.rmdir(subfolder_path)

def find_csv_and_template():
    csv_file = None
    template_file = None
    # Iterate over files in the upload folder
    for file in os.listdir(app.config['UPLOAD_FOLDER']):
        # Check if the file is a CSV file
        if file.lower().endswith('.csv'):
            csv_file = os.path.join(app.config['UPLOAD_FOLDER'], file)
        # Check if the file is a Markdown template file
        elif file.lower().endswith('.md'):
            template_file = os.path.join(app.config['UPLOAD_FOLDER'], file)
    return csv_file, template_file

if __name__ == '__main__':
    app.run(debug=True, port=8000)