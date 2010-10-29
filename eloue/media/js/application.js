var disableField = function(bool, field) {
    if (field.attr('type') != "hidden")
        parseInt(bool) ? field.removeAttr('disabled') : field.attr('disabled', 'disabled');
}

disableField($("input[name='exists']:checked").val(), $("input[name='password']")), 
$("input[name='exists']").change(function(event) {
    var radio = event.target;
    disableField(radio.value, $("input[name='password']"));
});

disableField($("input[name='1-exists']:checked").val(), $("input[name='1-password']")), 
$("input[name='1-exists']").change(function(event) {
    var radio = event.target;
    disableField(radio.value, $("input[name='1-password']"));
});