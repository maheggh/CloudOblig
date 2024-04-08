import os
from flask import Flask, request, render_template, send_file
from csvhandling import process_csv
import zipfile
from werkzeug.utils import secure_filename

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file part'
    
    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        return 'No selected file'

    if not uploaded_file.filename.lower().endswith('.zip'):
        return 'Invalid file type. Please upload a zip file.'

    zip_path = os.path.join(os.getcwd(), secure_filename(uploaded_file.filename))
    uploaded_file.save(zip_path)

    csv_filename = extract_csv_from_zip(zip_path)
    if not csv_filename:
        return 'No CSV file found in the zip.'

    output_zip_path = process_csv(csv_filename)

    return send_file(output_zip_path, as_attachment=True)

def extract_csv_from_zip(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        csv_files = [filename for filename in zip_ref.namelist() if filename.lower().endswith('.csv')]
        if csv_files:
            first_csv_filename = secure_filename(csv_files[0])
            extracted_csv_path = os.path.join(os.getcwd(), first_csv_filename)
            with zip_ref.open(csv_files[0]) as csv_file:
                with open(extracted_csv_path, 'wb') as f:
                    f.write(csv_file.read())
            return extracted_csv_path
        else:
            return None

if __name__ == '__main__':
    app.run(debug=True, port=8000)