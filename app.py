from flask import Flask, render_template, request, redirect, send_from_directory, send_file
from werkzeug.utils import secure_filename
from django.core.paginator import Paginator
from collections import defaultdict
import os 
import shutil

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
    create_folders()
    
    labels = os.listdir(app.config["DIRECTORY"])
    
    # Add pending files too? 
    if 'pending' in labels:
        labels.remove('pending')

    # Send total labels and files under those labels 
    stats = {}
    stats['labels'] = labels
    stats['count'] = []

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


# HELPER FUNCTIONS 
def create_text_files(filePath, promptsStr):
    # Create text file or override if it exists 
    file = open(filePath + '.txt', 'w')
    file.write(promptsStr)
    file.close()


def create_folders():
    labels = list(set(val['label'] for val in mappings.values()))
    print(labels)

    for i in labels:
        base_url = app.config["DIRECTORY"] + "/" + i
        print(base_url)

        # Create a directory and subdirectories 
        os.mkdir(base_url)
        os.mkdir(base_url + "/images")
        os.mkdir(base_url + "/prompts")

        # Move all the files to their respective image folders 
        contents = get_folder_contents(i)
        for file in contents: 
            shutil.move(app.config['UPLOAD_DIRECTORY'] + '/' + file, base_url + "/images/" + file)

            # Create all textfiles in the prompts section 
            create_text_files(base_url + "/prompts/" + file, mappings[file]["prompts"])


# Structure of the mapping 
# "filename" : [promptstr, label] 4KB for 100 

def get_folder_contents(label):
    reverse = defaultdict(list)
    for image, val in mappings.items():
        reverse[val["label"]].append(image)
    return reverse[label]


app.run()