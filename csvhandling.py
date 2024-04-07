import os
import csv
from jinja2 import Template
import shutil
import zipfile

def process_csv(csv_filename):
    # Get the absolute path to the directory containing the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, 'assets')

    # Read the template file
    template_path = os.path.join(assets_dir, 'template.md')
    with open(template_path, 'r') as file:
        template_str = file.read()

    # Create Jinja2 template object
    template = Template(template_str)

    # Output directory for generated Markdown files
    output_dir = os.path.join(script_dir, 'output')
    os.makedirs(output_dir, exist_ok=True)

    # Delete existing files in the output directory
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            os.unlink(os.path.join(root, file))

    # Generate Markdown files
    with open(csv_filename, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            filled_template = template.render(FirstName=row['FirstName'], LastName=row['LastName'])
            filename = os.path.join(output_dir, f"{row['FirstName']}_{row['LastName']}.md")
            with open(filename, 'w') as output_file:
                output_file.write(filled_template)

    print("Markdown files generated successfully.")

    # Create a zip file containing the generated Markdown files
    zip_file_path = shutil.make_archive(output_dir, 'zip', output_dir)
    return zip_file_path