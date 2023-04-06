
Dropzone.options.myDropzone= {
    url: '/upload',
    autoProcessQueue: false,
    uploadMultiple: true,
    parallelUploads: 10,
    maxFiles: 10,
    maxFilesize: 2000,
    acceptedFiles: 'image/*,video/*', 
    addRemoveLinks: true,
    dictDefaultMessage: "Drop files here OR Click here to select the file(s)",
    dictMaxFilesExceeded:"You can not upload any more files (maximum 10 files at once).",

    init: function() {
        dzClosure = this; // Makes sure that 'this' is understood inside the functions below.
        this.on("error", function(file, errorMessage) {
                        alert("error : " + errorMessage );
                    });

        // for Dropzone to process the queue (instead of default form behavior):
        document.getElementById("submit-all").addEventListener("click", function(e) {
            if ($("#form_upload")[0].checkValidity()){
                // Make sure that the form isn't actually being sent.
                e.preventDefault();
                e.stopPropagation();
                dzClosure.processQueue();
            } else {
                //Validate Form
                $("#form_upload")[0].reportValidity()
            }
        });

        //send all the form data along with the files:
        this.on("sendingmultiple", function(data, xhr, formData) {
            formData.append("task_name", jQuery("#task_name").val());
            formData.append("user_name", jQuery("#user_name").val());
            formData.append("email_adress", jQuery("#email_adress").val());
            formData.append("sensitivity", jQuery("#sensitivity").val());
        });
        // this.on("success", function(file) {
        //     if( $('#email_adress').val() ) {
        //         window.location.href="results_guest/"  + jQuery("#email_adress").val() + '/' + jQuery("#task_name").val()
        //     } else {
        //         window.location.href="results/"  + jQuery("#task_name").val()
        //     }
            
        // });
    }
}


