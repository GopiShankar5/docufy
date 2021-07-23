import imghdr
import os, re, os.path
from flask import Flask, render_template, request, redirect, url_for, abort, \
    send_from_directory
from werkzeug.utils import secure_filename
from flask_caching import Cache
import Text_Detection

config = {
    "DEBUG": True,          
    "CACHE_TYPE": "SimpleCache", 
    "CACHE_DEFAULT_TIMEOUT": 300
}

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 4160 * 3120
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'uploads'
app.config.from_mapping(config)
cache = Cache(app)
mypath = 'uploads'

def validate_image(stream):
    header = stream.read(512)  
    stream.seek(0)  
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')

@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_PATH'])
    return render_template('index.html', files=files)

@app.route('/', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS'] or \
                file_ext != validate_image(uploaded_file.stream):
            abort(400)
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
        Text_Detection.detection(filename)
    
    if request.form.get('submit_a'):
        cache.init_app(app)
        for root, dirs, files in os.walk(mypath):
            for file in files:
                os.remove(os.path.join(root, file))

    return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def upload(filename):
    image=send_from_directory(app.config['UPLOAD_PATH'], filename)
    return image