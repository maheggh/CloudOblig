import os
import csv
from jinja2 import Template
import shutil
import zipfile
from flask import current_app

def process_csv(csv_filename, template_filename):
    csv_dir = os.path.dirname(csv_filename)

    # Use the provided template file
    template_path = template_filename

    with open(template_path, 'r') as file:
        template_str = file.read()

    template = Template(template_str)

    output_dir = os.path.join(csv_dir, 'output')
    os.makedirs(output_dir, exist_ok=True)

    with open(csv_filename, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            filled_template = template.render(FirstName=row['FirstName'], LastName=row['LastName'])
            filename = os.path.join(output_dir, f"{row['FirstName']}_{row['LastName']}.md")
            with open(filename, 'w') as output_file:
                output_file.write(filled_template)

    zip_file_path = os.path.join(csv_dir, 'output.zip')
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), output_dir))

    return zip_file_path