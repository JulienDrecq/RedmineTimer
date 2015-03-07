$(document).ready(function(){
// FORM-NEW-TIMER
    $("#form-new-timer").submit( function() {
        // Init param
        var urlSubmit = $(this).attr('action');
        $('.start-timer').css("display", "none");
        $('.form-error').css("display", "none");
        $('.form-error').html('');
        $('.number-issue').css("display", "none");
        $.ajax({
            type: "POST",
            url: urlSubmit,
            data      : $(this).serializeArray(),
            beforeSend: function() {
                $('#form-loading').css("display", "block");
            },
            complete: function() {
                $('#form-loading').css("display", "none");
            },
            success: function(data) {
                if (data['error']) {
                    $('.form-error').html(data['value_error']);
                    $('.form-error').css("display", "block" );
                    $('.n-issue').css("display", "none");
                } else {
                    $('.form-error').html('');
                    $('.form-error').css("display", "none");
                    $('.link-issue').html(data['number-issue']);
                    $('.project-issue').html(data['project-issue']);
                    $('.name-issue').html(data['issue']);
                    $('.link-issue').attr('href', data['link-issue']);
                    $('.next-url').attr('href', data['next-url']);
                    $('.start-timer').css("display", "block");
                    $('.number-issue').css("display", "block");
                }
            },
            error: function() {
                $('.form-error').html("An error has occurred !");
                $('.number-issue').css("display", "none");
            }
        });
        return false;
    });
});

$('#new-timer').on('hidden.bs.modal', function (e) {
    //Reset modal when modal is close
    $("#form-new-timer :input[name='issue']").val('');
    $('.start-timer').css("display", "none");
    $('.form-error').css("display", "none");
    $('.form-error').html('');
    $('.number-issue').css("display", "none");
})