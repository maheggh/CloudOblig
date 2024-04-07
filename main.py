from flask import Flask, request, send_from_directory, jsonify, render_template
import os
import tarfile
import csv
import markdown2
from werkzeug.utils import secure_filename
from subprocess import call
import shutil

app = Flask(__name__)

UPLOAD_FOLDER = 'uploaded_files'
PROCESS_FOLDER = 'process_folder'
PDF_FOLDER = 'pdfs'
FINAL_TAR_FOLDER = 'final_tar'

# Ensure necessary directories exist
for folder in [UPLOAD_FOLDER, PROCESS_FOLDER, PDF_FOLDER, FINAL_TAR_FOLDER]:
    os.makedirs(folder, exist_ok=True)

def allowed_file(filename):
    return filename.endswith('.tar.gz')

def unpack_tar_gz(tar_gz_path, extract_path):
    with tarfile.open(tar_gz_path) as tar:
        tar.extractall(path=extract_path)

def pack_into_tar_gz(input_folder, output_path):
    with tarfile.open(output_path, "w:gz") as tar:
        tar.add(input_folder, arcname='.')

def convert_markdown_to_pdf(md_content, output_pdf_path):
    # Example using pandoc - adjust command as needed
    md_file_path = os.path.join(PROCESS_FOLDER, 'temp.md')
    with open(md_file_path, 'w') as md_file:
        md_file.write(md_content)
    call(['pandoc', md_file_path, '-o', output_pdf_path])

@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify(error="File part is missing"), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify(error="No file selected"), 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            tar_gz_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(tar_gz_path)

            # Unpack the .tar.gz
            unpack_tar_gz(tar_gz_path, PROCESS_FOLDER)

            # Process CSV and Markdown
            csv_path = os.path.join(PROCESS_FOLDER, 'persons.csv')
            md_template_path = os.path.join(PROCESS_FOLDER, 'template.md')
            with open(csv_path) as csv_file, open(md_template_path) as md_template_file:
                csv_reader = csv.DictReader(csv_file)
                md_template = md_template_file.read()
                for row in csv_reader:
                    md_content = md_template.format(**row)
                    pdf_path = os.path.join(PDF_FOLDER, f"{row['FirstName']}_{row['LastName']}.pdf")
                    convert_markdown_to_pdf(md_content, pdf_path)

            # Pack PDFs into a .tar.gz
            final_tar_gz_path = os.path.join(FINAL_TAR_FOLDER, 'final_output.tar.gz')
            pack_into_tar_gz(PDF_FOLDER, final_tar_gz_path)

            # Cleanup
            shutil.rmtree(PROCESS_FOLDER)
            shutil.rmtree(PDF_FOLDER)
            os.makedirs(PROCESS_FOLDER, exist_ok=True)
            os.makedirs(PDF_FOLDER, exist_ok=True)

            return send_from_directory(FINAL_TAR_FOLDER, os.path.basename(final_tar_gz_path), as_attachment=True)

        return jsonify(error="Invalid file"), 400

    return render_template('index.html')

@app.route('/upload-success')
def upload_success():
    return "File uploaded successfully!"

if __name__ == '__main__':
    app.run(debug=True)
