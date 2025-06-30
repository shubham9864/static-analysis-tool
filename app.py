from flask import Flask, render_template, request
import os
from werkzeug.utils import secure_filename
from analyzer import analyze_code  # Universal analyzer for .py, .cpp, .java

# --- Configuration ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'py', 'cpp', 'cc', 'cxx', 'c', 'java'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Helper: Check allowed extensions ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Create uploads directory if missing ---
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- Main Route ---
@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error_message = None

    if request.method == 'POST':
        try:
            if 'code_file' not in request.files:
                error_message = "No file part found in request."
                return render_template('index.html', error_message=error_message)

            file = request.files['code_file']

            if file.filename == '':
                error_message = "No file selected."
                return render_template('index.html', error_message=error_message)

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                # Analyze the uploaded file (any supported language)
                result = analyze_code(filepath)

                # Remove the file after analysis
                os.remove(filepath)
            else:
                error_message = "Only .py, .cpp, .java files are allowed."

        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"

    return render_template('index.html', result=result, error_message=error_message)

# --- Run Server ---
if __name__ == '__main__':
    app.run(debug=True)
