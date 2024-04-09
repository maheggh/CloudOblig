# import dependencies
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
import csv
import aiofiles
import zipfile
from uuid import uuid4
import shutil

# Initialize the FastAPI application
app = FastAPI()

# Define the directory paths for various stages of file handling
UPLOAD_FOLDER = 'uploaded_files'
PROCESSED_FOLDER = 'processed_files'
ZIP_FOLDER = 'zip_files'
TEMP_FOLDER = 'temp_files'

# Ensure the directories exist, or create them if they do not
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(ZIP_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)

# Set up the Jinja2 environment for template rendering
# Templates are loaded from TEMP_FOLDER where uploaded ZIP contents are extracted
env = Environment(
    loader=FileSystemLoader(TEMP_FOLDER),
    autoescape=select_autoescape()
)

# Process uploaded CSV and template to generate markdown files and zip them
async def process_csv_and_template(csv_file_path: str, template_name: str, file_id: str) -> str:
    processed_files = []

    # Load the Jinja2 template by name
    template = env.get_template(template_name)

    # Open and read the CSV file
    async with aiofiles.open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        content = await csvfile.read()
        reader = csv.DictReader(content.splitlines())

        # Process each row in the CSV file
        for row in reader:
            # Generate the filename and file path for the markdown file
            md_filename = f"{row['FirstName']}_{row['LastName']}.md"
            md_file_path = os.path.join(PROCESSED_FOLDER, md_filename)
            # Render the markdown content from the template with row data
            markdown_content = template.render(row)

            # Write the rendered content to the markdown file
            async with aiofiles.open(md_file_path, 'w', encoding='utf-8') as md_file:
                await md_file.write(markdown_content)
            processed_files.append(md_file_path)

    # Create a ZIP file of all processed markdown files
    zip_filename = f"{file_id}.zip"
    zip_file_path = os.path.join(ZIP_FOLDER, zip_filename)
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for file_path in processed_files:
            zipf.write(file_path, os.path.basename(file_path))

    return zip_file_path

# Endpoint to upload a ZIP file containing a markdown template and a CSV file
@app.post("/upload-zip/")
async def upload_zip(file: UploadFile = File(...)):
    # Ensure the uploaded file is a ZIP
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Invalid file extension.")
    
    # Generate a unique ID for the file and define its path
    file_id = str(uuid4())
    zip_path = os.path.join(UPLOAD_FOLDER, f"{file_id}.zip")

    # Save the uploaded ZIP file
    async with aiofiles.open(zip_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)

    # Extract the ZIP to get the template and CSV file
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(TEMP_FOLDER)
        for file_name in zipf.namelist():
            if file_name.endswith('.md'):
                template_name = file_name
            elif file_name.endswith('.csv'):
                csv_file_path = os.path.join(TEMP_FOLDER, file_name)
    
    # Process the template and CSV, then zip the results
    zip_file_path = await process_csv_and_template(csv_file_path, template_name, file_id)

    # Clean up the temporary folder
    shutil.rmtree(TEMP_FOLDER, ignore_errors=True)

    return {"file_id": file_id}

# Endpoint to download the processed ZIP file named 'output.zip'
@app.get("/download-zip/{file_id}")
async def download_zip(file_id: str):
    # Construct the file path and serve it if it exists
    zip_file_path = os.path.join(ZIP_FOLDER, f"{file_id}.zip")
    if os.path.exists(zip_file_path):
        return FileResponse(path=zip_file_path, media_type='application/zip', filename="output.zip")
    raise HTTPException(status_code=404, detail="File not found")

# Serve static files, useful for frontend applications
app.mount("/", StaticFiles(directory="static", html=True), name="static")
