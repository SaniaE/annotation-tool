from flask import Flask, render_template, request, redirect, send_from_directory, send_file
from werkzeug.utils import secure_filename
from django.core.paginator import Paginator
from helper import *
import os 
import shutil
import base64

app = Flask(__name__)

# App configs
app.config['DIRECTORY'] = 'uploads/'
app.config['UPLOAD_DIRECTORY'] = 'uploads/pending/'

global mappings
mappings = {} 

@app.route('/', methods=["GET", "POST"])
def home():
    global objects 
    objects = []
    prompt = []
    labels = []
    label = ""

    if os.path.isdir(app.config['DIRECTORY']) and os.path.isfile('dataset.zip'):
        shutil.rmtree(app.config['DIRECTORY'])
        os.remove('dataset.zip')
    
    if not os.path.exists(app.config['DIRECTORY']):
        os.makedirs(app.config['DIRECTORY'])
        os.makedirs(app.config['UPLOAD_DIRECTORY'])

    images = os.listdir(app.config['UPLOAD_DIRECTORY'])

    # Initializing keys for the mappings 
    if not mappings: 
        for i in images:
            mappings[i] = {}
            mappings[i]['prompts'] = ""
            mappings[i]['label'] = ""

    # Navigation
    if images:
        page = request.args.get('page', 1)

        paginator = Paginator(images, 1)
        objects = paginator.page(page)

        if mappings[objects[0]]['prompts'] != "":
            prompt = mappings[objects[0]]['prompts']
        
        labels = list(set(val['label'] for val in mappings.values()))
        label = mappings[objects[0]]['label']

    return render_template('index.html', images=list(objects), page=objects, prompts=prompt, labels=labels, label=label, allFiles=images)


# Saving images to the upload folder
@app.route('/upload', methods=["POST"])
def upload():
    files = request.files.getlist('file')

    if files:
        for i in files:
            i.save(os.path.join(app.config['UPLOAD_DIRECTORY'], secure_filename(i.filename)))

    return redirect('/')


# Serving the images on home page
@app.route('/serve/<filename>', methods=["GET"])
def serve(filename):
    return send_from_directory(app.config['UPLOAD_DIRECTORY'], filename)


# Deleting images from the uploads folder
@app.route('/delete/<filename>', methods=["GET"])
def delete(filename):
    file_path = os.path.join(app.config['UPLOAD_DIRECTORY'], filename)
    if os.path.isfile(file_path):
        os.remove(file_path)

    if objects.has_next():
        return redirect('/?page='+str(objects.number))
    elif len(os.listdir(app.config["UPLOAD_DIRECTORY"])) == 0:
        return redirect('/')
    else:
        return redirect('/dashboard')


@app.route('/dashboard')
def dashboard():
    create_folders(mappings, app)

    labels = os.listdir(app.config["DIRECTORY"])
    
    # Send total labels and files under those labels 
    stats = {}
    stats['labels'] = labels
    stats['count'] = []

    # Add pending files too
    if 'pending' in labels:
        pending_files = len(os.listdir(app.config["UPLOAD_DIRECTORY"]))
        if pending_files == 0:
            os.rmdir(app.config["UPLOAD_DIRECTORY"])
        else: 
            stats['pending'] = pending_files

        labels.remove('pending')

    # Create one to check number of images per label 
    for i in labels:
        folder_path = 'uploads/' + i + '/images'
        img_count = len(os.listdir(folder_path))
        stats['count'].append(img_count)
    
    return render_template('dashboard.html', stats=stats)


# Prompts 
@app.route('/prompt', methods=["POST", "GET"])
def prompt():
    # Get all the form data 
    fileName = request.form['image']
    labelName = request.form['label']

    promptsStr = ""
    for i in range(1, 11):
        promptsStr += request.form[fileName + '_' + str(i)] + '\n'

    # Saving properties to mappings
    mappings[fileName]['prompts'] = promptsStr
    mappings[fileName]['label'] = labelName

    if objects.has_next():
        return redirect('/?page='+str(objects.next_page_number()))
    else:
        return redirect('/dashboard')

# Download zip 
@app.route('/download', methods=["GET"])
def download():
    # Convert to zip 
    try:
        shutil.make_archive('dataset', 'zip', app.config['DIRECTORY'])
    except Exception as e:
        print(e)
    else:
        print("Zipping done")

    # Download
    return send_file('dataset.zip', as_attachment=True)


@app.route('/cleanup')
def cleanup():
    if os.path.isdir(app.config['DIRECTORY']):
        shutil.rmtree(app.config['DIRECTORY'])

    if os.path.isfile('dataset.zip'):
        os.remove('dataset.zip')

    return redirect('/')


@app.route('/crop', methods=["POST"])
def crop():
    img = request.form['dataURL']
    fileName = request.form['filename']

    imgData = base64.b64decode((img.split(','))[1])

    with open(os.path.join(app.config['UPLOAD_DIRECTORY'], fileName), 'wb') as file:
        file.write(imgData)
    file.close()

    return redirect('/')

app.run()