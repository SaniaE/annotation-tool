// FILE LIMIT 
tooltip = document.getElementById("tooltip");
inputFiles = document.getElementById("inputFiles");
submit = document.getElementById("submit")

if(inputFiles){
        inputFiles.addEventListener('change', ()=>{
        // Limiting to only 100 files 
        if(inputFiles.files.length > 100){
            submit.style.display = "none"
            tooltip.style.display = ""
        }
        else{
            submit.style.display = ""
            tooltip.style.display = "none"
        }
    });
}

// LABEL FILTERS
filters = document.getElementById("filters");
filter = document.getElementsByClassName("filter");
label = document.getElementById("label");
add = document.getElementById("add");

labels = [];

Array.from(filter).forEach(element => {
    labels.push(element.id);    
});

// Clickable or hoverable suggestions
Array.from(filter).forEach(element => {
    element.addEventListener('hover', ()=>{
        label.value = element.id;
    });
    element.addEventListener('click', ()=>{
        label.value = element.id;
    });
});

add.addEventListener('hover', ()=>{
    filters.style.display = "none";
});

add.addEventListener('click', ()=>{
    filters.style.display = "none";
});

// Filters
label.addEventListener('input', (e)=>{
    val = e.target.value;

    if(val == ""){
        filters.style.display = "none";
    }
    else{
        filters.style.display = "";
    }

    if(!labels.includes(val.toLowerCase())){
        add.style.display = "";
    }

    for (i = 0; i < labels.length; i++) {
        if (labels[i].toLowerCase().indexOf(val) > -1) {
            filter[i].style.display = "";
        } 
        else {
            filter[i].style.display = "none";
        }
    }
});

// CROPPER
cropImage = document.getElementById("crop");
copy = document.getElementById("copy");

// Parameter variables
image = "";
var cropper; 
copyBool = false;

// Creating copies of cropped image
copy.addEventListener('change', ()=>{
    copyBool = copy.checked;
})

cancel = document.getElementById("cancel");

// Cropper instances 
cropImage.addEventListener('click', ()=>{
    if(cropImage.innerText == "Crop"){   
        copy.style.display = "";
        cropImage.innerText = "Save Image";
        cancel.style.display = "";

        image = document.getElementById(cropImage.value);
        cropper = new Cropper(image, {
            aspectRatio: 0, 
            viewMode: 0
        })
    }
    else{
        croppedImage = cropper.getCroppedCanvas().toDataURL('image/png');

        // Send the image data to be saved 
        xhr = new XMLHttpRequest();
        xhr.open('POST', '/crop', true);
        xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        xhr.send(`dataURL=${encodeURIComponent(croppedImage)}&filename=${image.id}&copy=${copyBool}`);
        
        location.reload();
        location.reload();

        // Cleanup 
        cropper.destroy();
        location.reload();
    }
});

cancel.addEventListener('click', ()=>{
    cropper.destroy();
    cancel.style.display = "none";
});