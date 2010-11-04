$(document).ready(function() {
    var exists = $("input[name$='exists']:checked").val();
    var passwordInput = $("input[name$='password']");
    if (passwordInput.attr('type') != 'hidden') {
        if (parseInt(exists, 10)) { 
            passwordInput.removeAttr('disabled');
        } else {
            passwordInput.attr('disabled', 'disabled');
        }
    }
    $("input[name$='exists']").change(function(event) {
       var radio = $(event.target);
       if (passwordInput.attr('type') != 'hidden') {
           if (parseInt(radio.val(), 10)) { 
               passwordInput.removeAttr('disabled');
           } else {
               passwordInput.attr('disabled', 'disabled');
           }
       } 
    });
    
    var phoneSelect = $("select[name$='phones']");
    var phoneInput = $("input[name$='phones__phone']");
    if (phoneSelect.val() && phoneInput.attr('type') != 'hidden') {
        phoneInput.attr('disabled', 'disabled');
    }
    phoneSelect.change(function(event) {
       var option = $(event.target);
       if (option.val() && phoneInput.attr('type') != 'hidden') {
           phoneInput.attr('disabled', 'disabled');
       } else {
           phoneInput.removeAttr('disabled');
       }       
    });
    
    var addressSelect = $("select[name$='addresses']");
    var addressInput = $(["input[name*='addresses__']", "textarea[name*='addresses__']", "select[name*='addresses__']"]);
    if (addressSelect.val() && addressInput.attr('type') != 'hidden') {
        addressInput.each(function(i, el) {
            $(el).attr('disabled', 'disabled');
        });
    }
    addressSelect.change(function(event) {
       var option = $(event.target);
       if (option.val() && addressInput.attr('type') != 'hidden') {
           addressInput.each(function(i, el) {
               $(el).attr('disabled', 'disabled');
           });
       } else {
           addressInput.each(function(i, el) {
               $(el).removeAttr('disabled');
           });
       }
    });
     
    $('#id_0-started_at_0').datepicker({
        dateFormat: 'dd/mm/yy',
        minDate: 0,
        maxDate: '+360d',
        onSelect: function(dateText, inst) {
    	    var ended_at = $('#id_0-ended_at_0');
    	    ended_at.val(dateText);
    	    ended_at.datepicker( "option", "minDate", dateText);
    	}
    });
    
    $('#id_0-ended_at_0').datepicker({
        dateFormat: 'dd/mm/yy'
    });
});