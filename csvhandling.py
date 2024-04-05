import os
import csv
from jinja2 import Template

# Get the absolute path to the directory containing the script
script_dir = os.path.dirname(os.path.abspath(__file__))
assets_dir = os.path.join(script_dir, 'assets')

# Read the template file
template_path = os.path.join(assets_dir, 'template.md')
with open(template_path, 'r') as file:
    template_str = file.read()

# Create Jinja2 template object
template = Template(template_str)

# Path to CSV file
csv_path = os.path.join(assets_dir, 'personas.csv')

# Read names from CSV and generate Markdown files
with open(csv_path, 'r', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        # Fill in the template with values from CSV
        filled_template = template.render(FirstName=row['FirstName'], LastName=row['LastName'])
        
        # Generate filename (e.g., John_Doe.md)
        filename = os.path.join(script_dir, f"{row['FirstName']}_{row['LastName']}.md")
        
        # Write filled template to Markdown file
        with open(filename, 'w') as output_file:
            output_file.write(filled_template)

print("Markdown files generated successfully.")