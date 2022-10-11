Dropzone.options.myDropzone= {
            url: 'upload',
            autoProcessQueue: false,
            uploadMultiple: true,
            parallelUploads: 5,
            maxFiles: 5,
            maxFilesize: 2000,
            acceptedFiles: 'image/*,video/*', 
            addRemoveLinks: true,
            init: function() {
                dzClosure = this; // Makes sure that 'this' is understood inside the functions below.

                // for Dropzone to process the queue (instead of default form behavior):
                document.getElementById("submit-all").addEventListener("click", function(e) {
                    // Make sure that the form isn't actually being sent.
                    e.preventDefault();
                    e.stopPropagation();
                    dzClosure.processQueue();
                });

                //send all the form data along with the files:
                this.on("sendingmultiple", function(data, xhr, formData) {
                    formData.append("username", jQuery("#username").val());
                });
                this.on("queuecomplete", function(file) {
                    window.location.href="result/" + jQuery("#username").val()
                });
            }
        }