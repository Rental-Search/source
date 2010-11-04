var disableField = function(bool, field) {
    if (field.attr('type') != "hidden")
        parseInt(bool) ? field.removeAttr('disabled') : field.attr('disabled', 'disabled');
}

disableField($("input[name='0-exists']:checked").val(), $("input[name='0-password']")), 
$("input[name='0-exists']").change(function(event) {
    var radio = event.target;
    disableField(radio.value, $("input[name='0-password']"));
});

disableField($("input[name='1-exists']:checked").val(), $("input[name='1-password']")), 
$("input[name='1-exists']").change(function(event) {
    var radio = event.target;
    disableField(radio.value, $("input[name='1-password']"));
});


    var minDateValue;
    var maxDateValue;
    
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
	
