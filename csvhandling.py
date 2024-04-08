import os
import csv
from jinja2 import Template
import shutil
import zipfile

def process_csv(csv_filename):
    # Get the directory containing the CSV file
    csv_dir = os.path.dirname(csv_filename)

    # Find any markdown file in the same directory as the CSV file
    markdown_files = [f for f in os.listdir(csv_dir) if f.endswith('.md')]
    if not markdown_files:
        return "No markdown file found in the directory."

    # Use the first markdown file found as the template
    template_path = os.path.join(csv_dir, markdown_files[0])
    with open(template_path, 'r') as file:
        template_str = file.read()

    # Create Jinja2 template object
    template = Template(template_str)

    # Output directory for generated Markdown files
    output_dir = os.path.join(csv_dir, 'output')
    os.makedirs(output_dir, exist_ok=True)

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
    zip_file_path = os.path.join(csv_dir, 'output.zip')
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for root, dirs, files in os.walk(output_dir):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), output_dir))

    return zip_file_path