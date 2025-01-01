from flask import Flask, request, redirect, url_for, flash, jsonify, render_template
import os
import logging
import re
from PIL import Image
import pytesseract

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'C:/New folder/htdocs/algo/uploads'  # Define the upload folder
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.secret_key = 'supersecretkey'  # Needed for flashing messages

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def upload_form():
    return render_template('upload_form.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        logging.info('No file part in request')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        logging.info('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        logging.info(f'File saved to {file_path}')
        
        # Perform OCR and approval decision
        approval_results = process_image(file_path)
        return render_template('tenant_approval.html', approval_results=approval_results)
    else:
        flash('File type not allowed')
        logging.info('File type not allowed')
        return redirect(request.url)

def process_image(image_path):
    # Path to the Tesseract executable (update if necessary)
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    # Open the image
    img = Image.open(image_path)

    # Perform OCR on the image to extract text
    text = pytesseract.image_to_string(img)

    # Use regular expressions to find all numbers in the extracted text
    numbers = re.findall(r'\d+', text)

    # Convert the extracted numbers to a list of integers (assuming these are incomes)
    income_list = [int(num) for num in numbers]

    # Define your income threshold for approval (for example, $40,000)
    income_threshold = 40000

    # Create a list to store approval decisions
    approval_decisions = []

    # Determine approval based on income
    for income in income_list:
        if income >= income_threshold:
            approval_decisions.append({'income': income, 'decision': 'Approved'})
        else:
            approval_decisions.append({'income': income, 'decision': 'Denied'})

    return approval_decisions

if __name__ == '__main__':
    app.run(debug=True)

