import os
import shutil
from collections import defaultdict

# HELPER FUNCTIONS 
def create_text_files(filePath, promptsStr):
    # Create text file or override if it exists 
    file = open(filePath + '.txt', 'w')
    file.write(promptsStr)
    file.close()


def create_folders(mappings, app):
    labels = list(set(val['label'] for val in mappings.values()))
    
    if '' in labels:
        labels.remove("")
    
    for i in labels:
        base_url = app.config["DIRECTORY"] + i

        if not os.path.exists(base_url):
            # Create a directory and subdirectories 
            os.mkdir(base_url)
            os.mkdir(base_url + "/images")
            os.mkdir(base_url + "/prompts")

        # Move all the files to their respective image folders 
        contents = get_folder_contents(i, mappings)
        for file in contents: 
            shutil.move(app.config['UPLOAD_DIRECTORY'] + '/' + file, base_url + "/images/" + file)

            # Create all textfiles in the prompts section 
            create_text_files(base_url + "/prompts/" + file, mappings[file]["prompts"])


def get_folder_contents(label, mappings):
    reverse = defaultdict(list)
    for image, val in mappings.items():
        reverse[val["label"]].append(image)
    return reverse[label]


# TODO: Add rename functionality
def rename(app):
    folders = os.listdir(app.config["DIRECTORY"]).remove("pending")

    for i in folders:
        # Add per label rename 
        pass
