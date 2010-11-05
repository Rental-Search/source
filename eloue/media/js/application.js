$(document).ready(function() {
    var bool = $("input[name$='exists']:checked").val();
    var field = $("input[name$='password']");
    if (field.attr('type') != 'hidden') {
        if (parseInt(bool, 10)) { 
            field.removeAttr('disabled');
        } else {
            field.attr('disabled', 'disabled');
        }
    }

    $("input[name$='exists']").change(function(event) {
       var radio = event.target;
       if (field.attr('type') != 'hidden') {
           if (parseInt(radio.value, 10)) { 
               field.removeAttr('disabled');
           } else {
               field.attr('disabled', 'disabled');
           }
       } 
    });

    $('#id_0-started_at_0').datepicker({
        dateFormat: 'dd/mm/yy',
        minDate: 0,
        maxDate: '+360d',
        onSelect: function(dateText, inst) {
            $('#id_0-ended_at_0').val(dateText);
            $( "#id_0-ended_at_0" ).datepicker( "option", "minDate", dateText);
        }
    });
    
    $('#id_0-ended_at_0').datepicker({
        dateFormat: 'dd/mm/yy',
        maxDate: '+85d'
    });
});