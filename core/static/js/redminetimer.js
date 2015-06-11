// NEW TIMER
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
});
// END NEW TIMER

// FILTER DATE
$('#sandbox-start-date .input-group.date').datepicker({
    format: "yyyy-mm-dd",
    autoclose: true,
    todayHighlight: true,
    orientation: "top auto"
});

$('#sandbox-end-date .input-group.date').datepicker({
    format: "yyyy-mm-dd",
    autoclose: true,
    todayHighlight: true,
    orientation: "top auto"
});

$('#sandbox-edit-entry .input-group.date').datepicker({
    format: "yyyy-mm-dd",
    autoclose: true,
    todayHighlight: true,
    orientation: "top auto"
});

$('#filter-date').on('hidden.bs.modal', function (e) {
    //Reset modal when modal is close
    $("#form-filter-date :input[name='start_date']").val('');
    $("#form-filter-date :input[name='end_date']").val('');
});
// END FILTER DATE

// TIMER
var TimerIssue = new (function() {
    var $stopwatch, // Stopwatch element on the page
        currentTime = 0, // Current time in hundredths of a second
        updateTimer = function() {
            $stopwatch.html(formatTime(++currentTime));
        },
        init = function() {
            $stopwatch = $('#stopwatch');
            TimerIssue.Timer = $.timer(updateTimer, 1000, false);
        };
    this.resetStopwatch = function() {
        currentTime = -1;
        this.Timer.stop().once();
        var $button_save = $('#button_save');
        $button_save.css('display', 'none');
        var $button_reset = $('#button_reset');
        $button_reset.css('display', 'none');
    };
    this.toggle = function() {
        this.Timer.toggle();
        var $play_pause_timer = $('#play_pause_timer');
        var $button_save = $('#button_save');
        $button_save.css('display', 'inline-block');
        var $button_reset = $('#button_reset');
        $button_reset.css('display', 'inline-block');
        $play_pause_timer.children('.timer-text').text('');
        if (this.Timer.isActive) {
            $play_pause_timer.removeClass('btn-success').addClass('btn-warning');
            $play_pause_timer.children('.glyphicon').removeClass('glyphicon-play').addClass('glyphicon-pause');
        } else {
            $play_pause_timer.removeClass('btn-warning').addClass('btn-success');
            $play_pause_timer.children('.glyphicon').removeClass('glyphicon-pause').addClass('glyphicon-play');
        }
    };
    $(init);
});
// END TIMER

// functions
function pad(number, length) {
    var str = '' + number;
    while (str.length < length) {str = '0' + str;}
    return str;
}

function formatTime(time) {
    var hours = parseInt(time / 6000),
        min = parseInt(time / 60) - (hours * 60),
        sec = time - (min * 60) - (hours * 6000);
    if (hours == 0 && min == 0) {
        return sec + " sec"
    } else if (hours == 0) {
        return pad(min, 2) + ":" + pad(sec, 2) + " min"
    } else {
        return pad(hours, 2) + ":" + pad(min, 2) + ":" + pad(sec, 2)
    }
}