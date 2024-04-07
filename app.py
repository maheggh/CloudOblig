from flask import Flask, request, render_template, send_file
from csvhandling import process_csv

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    csvfile = request.files['csvfile']
    csv_filename = 'uploads/personas.csv'  # Corrected filename
    csvfile.save(csv_filename)

    # Process the uploaded CSV file
    output_zip_path = process_csv(csv_filename)

    # Send the generated zip file as a response
    return send_file(output_zip_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=8000)