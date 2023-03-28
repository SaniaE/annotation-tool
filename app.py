from flask import Flask, render_template, request, redirect, send_from_directory, send_file
from werkzeug.utils import secure_filename
from django.core.paginator import Paginator
from helper import *
import os 
import shutil
import base64
import random

app = Flask(__name__)

# App configs
app.config['DIRECTORY'] = 'uploads/'
app.config['UPLOAD_DIRECTORY'] = 'uploads/pending/'

global mappings
mappings = {} 

@app.route('/', methods=["GET", "POST"])
def home():
    initialize(app)
    global objects 
    objects = []
    prompt = []
    labels = []
    label = ""

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

    del mappings[filename]

    if objects.has_next():
        return redirect('/?page='+str(objects.number))
    elif len(os.listdir(app.config["UPLOAD_DIRECTORY"])) == 0:
        return redirect('/')
    else:
        return redirect('/dashboard')


@app.route('/dashboard')
def dashboard():
    labels = list(set(val['label'] for val in mappings.values()))

    # Send total labels and files under those labels 
    stats = {}
    stats['count'] = []

    # Create one to check number of images per label 
    for i in labels:
        stats['count'].append(len(get_folder_contents(i, mappings)))
    
    if '' in labels:
        labels[labels.index('')] = "Pending prompts"

    stats['labels'] = labels

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
    create_folders(mappings, app)

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
    copyFile = request.form['copy']

    # Saving crops 
    if copyFile == "true":
        newName = fileName.split('.')[0] + str(random.randint(1, 100)) + '.' + fileName.split('.')[1]
        if not os.path.exists(app.config['UPLOAD_DIRECTORY'] + newName):
            shutil.copy2(app.config['UPLOAD_DIRECTORY'] + fileName, app.config['UPLOAD_DIRECTORY'] + newName)
        else:
            newName = fileName.split('.')[0] + str(random.randint(1, 100)) + str(random.randint(1, 100)) + '.' + fileName.split('.')[1]
            shutil.copy2(app.config['UPLOAD_DIRECTORY'] + fileName, app.config['UPLOAD_DIRECTORY'] + newName)

    mappings[newName] = {}
    mappings[newName]['prompts'] = ""
    mappings[newName]['label'] = ""

    imgData = base64.b64decode((img.split(','))[1])

    with open(os.path.join(app.config['UPLOAD_DIRECTORY'], fileName), 'wb') as file:
        file.write(imgData)
    file.close()

    return redirect('/')

app.run()