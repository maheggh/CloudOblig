import os
import csv
from jinja2 import Template
import zipfile
from flask import current_app

def process_csv(csv_filename, template_filename):
    # Define the directory where the output files will be saved
    output_dir = os.path.join(current_app.root_path, 'output')
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Use the provided template file
    template_path = template_filename

    # Read the contents of the template file
    with open(template_path, 'r') as file:
        template_str = file.read()

    # Create a Jinja2 template object
    template = Template(template_str)

    # Open the CSV file
    with open(csv_filename, 'r', newline='') as csvfile:
        # Create a CSV reader object
        reader = csv.DictReader(csvfile)
        # Iterate over each row in the CSV file
        for row in reader:
            # Render the template with the data from the current row
            filled_template = template.render(FirstName=row['FirstName'], LastName=row['LastName'])
            # Define the filename for the output Markdown file
            filename = os.path.join(output_dir, f"{row['FirstName']}_{row['LastName']}.md")
            # Write the rendered template to the output Markdown file
            with open(filename, 'w') as output_file:
                output_file.write(filled_template)

    # Define the path for the output ZIP file
    zip_file_path = os.path.join(current_app.root_path, 'output.zip')
    # Create a new ZIP file
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        # Recursively add all files in the output directory to the ZIP file
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), output_dir))

    # Return the path to the output ZIP file
    return zip_file_path