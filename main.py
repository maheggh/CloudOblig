#import
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import csv
import aiofiles
import zipfile
from uuid import uuid4

# Create a new FastAPI application instance
app = FastAPI()

# Define constants for directory paths to be used in the app
UPLOAD_FOLDER = 'uploaded_files'
PROCESSED_FOLDER = 'processed_files'
ZIP_FOLDER = 'zip_files'
TEMP_FOLDER = 'temp_files'

# Create the above directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(ZIP_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)

# Function to process CSV file and generate markdown files using the markdown template
async def process_csv(csv_file_path: str, template_content: str, file_id: str) -> str:
    processed_files = []
    # Open CSV file and read its contents
    async with aiofiles.open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        content = await csvfile.read()
        # Read the CSV file and convert it to dictionary format
        reader = csv.DictReader(content.splitlines())
        # For each row in the CSV file, generate a markdown file
        for row in reader:
            # Extract first and last names
            first_name = row.get('FirstName', '')
            last_name = row.get('LastName', '')
            # If both first and last names are provided, create the markdown file
            if first_name and last_name:
                # Create the file name
                md_filename = f"{first_name}_{last_name}.md"
                # Create the full path for the markdown file
                md_file_path = os.path.join(PROCESSED_FOLDER, md_filename)
                # Format the template with data from the CSV row
                markdown_content = template_content.format(**row)
                # Write the formatted content to the markdown file
                async with aiofiles.open(md_file_path, 'w', encoding='utf-8') as md_file:
                    await md_file.write(markdown_content)
                # Add the path to the list of processed files
                processed_files.append(md_file_path)
    
    # Create a ZIP file containing all the processed markdown files
    zip_filename = f"{file_id}.zip"
    zip_file_path = os.path.join(ZIP_FOLDER, zip_filename)
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        # Add each processed file to the ZIP
        for file in processed_files:
            zipf.write(file, os.path.basename(file))
    
    # Remove processed markdown files after adding them to the ZIP
    for file in processed_files:
        os.remove(file)
    
    # Return the path of the created ZIP file
    return zip_file_path

# Define endpoint for uploading a ZIP file
@app.post("/upload-zip/")
async def upload_zip(file: UploadFile = File(...)):
    # Ensure the uploaded file is a ZIP file
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Invalid file extension.")
    
    # Generate a unique ID for the file
    file_id = str(uuid4())
    # Create a path for the uploaded ZIP file
    zip_path = os.path.join(UPLOAD_FOLDER, f"{file_id}.zip")
    
    # Save the uploaded ZIP file to the filesystem
    async with aiofiles.open(zip_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    
    # Initialize placeholders for the markdown template and CSV file path
    template_content = ""
    csv_file_path = ""
    
    # Extract the ZIP file to access its contents
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(TEMP_FOLDER)
        # Identify the markdown template and CSV file within the extracted contents
        for file_name in zipf.namelist():
            if file_name.endswith('.md'):
                template_path = os.path.join(TEMP_FOLDER, file_name)
                async with aiofiles.open(template_path, 'r') as template_file:
                    template_content = await template_file.read()
            elif file_name.endswith('.csv'):
                csv_file_path = os.path.join(TEMP_FOLDER, file_name)
    
    # Check if both a markdown template and CSV file were found
    if not template_content or not csv_file_path:
        raise HTTPException(status_code=400, detail="ZIP does not contain both .md and .csv files.")
    
    # Process the CSV file using the markdown template
    zip_file_path = await process_csv(csv_file_path, template_content, file_id)
    
    # Clean up temporary files
    os.remove(zip_path)
    os.remove(template_path)
    os.remove(csv_file_path)
    
    # Respond with the unique ID of the processed ZIP file for downloading
    return {"file_id": file_id}

# Define endpoint for downloading the processed ZIP file
@app.get("/download-zip/{file_id}")
async def download_zip(file_id: str):
    # Construct the full path of the ZIP file to download
    zip_file_path = os.path.join(ZIP_FOLDER, f"{file_id}.zip")
    # Serve the file if it exists
    if os.path.exists(zip_file_path):
        return FileResponse(
            path=zip_file_path, 
            media_type='application/zip', 
            filename="output.zip"  # Suggests the download filename to be "output.zip"
        )
    # Respond with a 404 error if the file does not exist
    raise HTTPException(status_code=404, detail="File not found")

# Serve static files, such as the HTML and CSS for the web interface
app.mount("/", StaticFiles(directory="static", html=True), name="static")
