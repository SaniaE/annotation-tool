import os
import shutil
from collections import defaultdict

# HELPER FUNCTIONS 
# Initialize folders and cleanup for the application
def initialize(app):
    if not os.path.exists(app.config['DIRECTORY']):
        os.makedirs(app.config['DIRECTORY'])
        os.makedirs(app.config['UPLOAD_DIRECTORY'])


# Create text file or override if it exists 
def create_text_files(filePath, promptsStr):
    file = open(filePath + '.txt', 'w')
    file.write(promptsStr)
    file.close()


# Sort images into folders as per labels 
def create_folders(mappings, app):
    labels = list(set(val['label'] for val in mappings.values()))
    
    if '' in labels:
        labels.remove("")
    
        for i in labels:
            # Add folder name safety 
            if len(i.split()) > 2:
                for c in i.split():
                    i += c + '_'

            base_url = app.config["DIRECTORY"] + i

            # Create a directory and subdirectories 
            if not os.path.exists(base_url):
                os.mkdir(base_url)
                os.mkdir(base_url + "/images")
                os.mkdir(base_url + "/prompts")

            # Move all the files to their respective image folders 
            contents = get_folder_contents(i, mappings)
            for file in contents: 
                shutil.move(app.config['UPLOAD_DIRECTORY'] + '/' + file, base_url + "/images/" + file)

                # Create all textfiles in the prompts section 
                create_text_files(base_url + "/prompts/" + file.split('.')[0], mappings[file]["prompts"])
    else:
        if len(os.listdir(app.config["UPLOAD_DIRECTORY"])) == 0:
            os.rmdir(app.config["UPLOAD_DIRECTORY"])


# Group images per label
def get_folder_contents(label, mappings):
    reverse = defaultdict(list)
    for image, val in mappings.items():
        reverse[val["label"]].append(image)
    return reverse[label]