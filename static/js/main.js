$(document).ready(function () {
    // Init
    var togglePassword = document.querySelector('#togglePassword');
    var password = document.querySelector('#password');


    $('.image-section').hide();
    $('.loader').hide();
    $('#result').hide();
    $('#btn-predict').hide();

    // Upload Preview
    function readURL(input) {
        if (input.files && input.files[0]) {
            var reader = new FileReader();
            reader.onload = function (e) {
                $('#imagePreview').css('background-image', 'url(' + e.target.result + ')');
                $('#imagePreview').hide();
                $('#imagePreview').fadeIn(650);
            }
            reader.readAsDataURL(input.files[0]);
        }
    }



    $("#imageUpload").change(function () {
        $('.image-section').show();
        $('#result').text('');
        $('#symptoms').text('');
        $('#solution').text('');
        $('#result').hide();
        $('#symptoms').hide();
        $('#solution').hide();
        readURL(this);
    });

    // Predict

//    $('#btn-predict').click(function () {
//
//        window.location.replace("http://127.0.0.1:5000/disease-info");
//
//
//    });


    $('#btn-upload').click(function () {
        var form_data = new FormData($('#upload-file')[0]);

        // Show loading animation
        $(this).hide();
        $('.loader').show();

        // Make prediction by calling api /predict
        $.ajax({
            type: 'POST',
            url: '/predict',
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            async: true,
            success: function (data) {
                // Get and display the result

                $('#btn-predict').show();
                console.log('Success!');
            },
        });
    });

});

