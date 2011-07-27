jQuery.fn.reverse = function() {
  return this.pushStack(this.get().reverse(), arguments);
};

$(document).ready(function() {
    // Password field enabler/disabler
    var passwordInput,
    paypalEmailInput,
    isProfessionalInput,
    companyNameInput,
    phoneSelect,
    phoneInput,
    addressSelect,
    addressInput,
    bookingCreate,
    bookingPrice,
    notification,
    disabledDays; //added attr
    var exists = $("input[name$='exists']:checked").val();
    passwordInput = $("input[name$='password']");
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
    $("input[name$='old_password']").removeAttr('disabled');

    // Email PayPal account enable/disable
    /*paypalEmailInput = $("input[name$='paypal_email']");
    if (paypalEmailInput.attr('type') != 'hidden') {
        if (parseInt(exists, 10)) {
            paypalEmailInput.removeAttr('disabled');
        } else {
            paypalEmailInput.attr('disabled', 'disabled');
        }
    }*/
    
    $("input[name$='exists']").change(function(event) {
        var radio = $(event.target);
        if (paypalEmailInput.attr('type') != 'hidden') {
            if (parseInt(radio.val(), 10)) {
                paypalEmailInput.removeAttr('disabled');
            } else {
                paypalEmailInput.attr('disabled', 'disabled');
            }
        }
    });
    
    // Company name field display/none
    isProfessionalInput = $("input[name$='is_professional']");
    companyNameInput = $(".company-name");
    companyNameInput.hide();

    var exists = $("input[name$='is_professional']:checked").val();

    if (exists == 'on') {
        companyNameInput.show();
    }
    $(":checkbox").click(function() {
        if (isProfessionalInput.is(':checked')) {
            companyNameInput.show();
        } else {
            companyNameInput.hide();
        }
    });

    // Phone field enabler/disabler
    phoneSelect = $("select[name$='phones']");
    phoneInput = $("input[name$='phones__phone']");
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

    // Address field enabler/disabler
    addressSelect = $("select[name$='addresses']");
    addressInput = $(["input[name*='addresses__']", "textarea[name*='addresses__']", "select[name*='addresses__']"]);
    // New number field display/none
    if($("#select_phone").length==1){	
	newPhoneInput = $(".add_new_phone");
	newPhoneInput.hide();
 	$("a#link_add_phone").click(function(){		
		newPhoneInput.show();	
		$("select[id$='-phones']").val('---------');
		phoneInput.removeAttr('disabled');		
 	});
    }

    // New adress field display/none
    if($("#select_addr").length==1){    	
	newAddrInput = $(".add_new_addr");
	newAddrInput.hide();
	$("a#link_add_addr").click(function(){		
		newAddrInput.show();	
		$("select[id$='-addresses']").val('---------');
		addressInput.each(function(i, el) {
            $(el).removeAttr('disabled');
        });
	});
    }
    
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
    
    var url = window.location.href;
    var array = url.split("-");
    var booking_id = array[array.length-1].split("/")[0];
    if (booking_id) {
        $.get('occupied_date/', {"booking_id": booking_id},
            function(data) {
                disabledDays = data;
            }, 'json');
    }
    /* utility functions */
    function occupiedDays(date) {
      var m = date.getMonth(), d = date.getDate(), y = date.getFullYear();
      for (i = 0; i < disabledDays.length; i++) {
        if($.inArray(y +'-'+ (m+1) + '-' + d, disabledDays) != -1 || new Date() > date) {
          return [false];
        }
      }
      return [true];
    }
    
    // Price calculations
    bookingPrice = function(form) {
        var template,
        serializedForm;
        template = '{{#errors}}{{ errors }}{{/errors}}{{^errors}}<p>Total :<span class="day">{{ duration }},</span> soit <span class="total-price">{{ total_price }}</span></p>{{/errors}}';
        serializedForm = $.grep(form.serializeArray(),
        function(el) {
            return (el.name.indexOf('csrfmiddlewaretoken') != -1) || (el.name.indexOf('wizard_step') != -1);
        },
        true);
        $.ajax({
            type: 'GET',
            url: 'price/',
            dataType: 'json',
            data: $.param(serializedForm),
            success: function(data) {
                $("#booking-total").html(Mustache.to_html(template, data));
            }
        });
    }
    
    // Date picker
    $('input[name$=started_at_0]').datepicker({
        dateFormat: 'dd/mm/yy',
        minDate: 1,
        maxDate: '+360d',
        beforeShowDay: occupiedDays,
        onSelect: function(dateText, inst) {
            
            var date1 = $(this).datepicker('getDate');
            
            var date = new Date( Date.parse( date1 ) ); 
            date.setDate( date.getDate() + 1 );
            
            var newDate = date.toDateString(); 
            newDate = new Date( Date.parse( newDate ) );
            
            var ended_at = $('input[name$=ended_at_0]');

            ended_at.datepicker("option", "minDate", newDate);
            
            ended_at.datepicker('setDate', newDate );
            
            bookingPrice($('#booking_create'));
        }
    });
    
    $('input[name$=ended_at_0]').datepicker({
        dateFormat: 'dd/mm/yy',
        beforeShowDay: occupiedDays,
    });
    
    bookingCreate = $('#booking_create');
    if (bookingCreate.length > 0) {
        bookingPrice(bookingCreate);
    }
    
    $('#booking_create').change(function(event) {
        bookingPrice($(this));
    });
    
    // Confirm booking rejection
    $('form.bk-refuse').submit(function(event) {
        return confirm('Êtes-vous sûr de vouloir refuser cette location ?');
    });
    
    $('#alert-delete').submit(function(event) {
        return confirm('Êtes-vous sûr de vouloir supprimer cette alerte ?');
    });
    
    $('#product-delete').submit(function(event) {
        return confirm('Êtes-vous sûr de vouloir supprimer cet objet ?');
    });
    
    //Flash message slidedown
    notification = $("#notification");
    if (notification.html()) {
        notification.slideDown("slow");
        setTimeout('hideNotification()',
        4000
        // 4 seconds
        );
        notification.click(function() {
            hideNotification();
        });
    }
    
    // Put the cursor at the beginning of the textarea

    /* to the BEGIN */

    $('#id_body').each(function(){ //change event or something you want

    /* simple js */
    if (this.createTextRange) {
     var r = this.createTextRange();
     r.collapse(true);
     r.select();
    }

     $(this).focus(); //set focus

    });
    
    //Partner slideshow
    $('.slide').cycle({
        fx: 'fade',
        timeout: 6000,
        cleartype: true,
        cleartypeNoBg: true
    });

    //add in product_create
    $(".tabsPrices").tabs();

    // DatePicker for season price
    $('#new-start-date').datepicker({
        dateFormat: 'dd/mm'
    });

    $('#new-end-date').datepicker({
        dateFormat: 'dd/mm'
    });
    
    $(".calculator a").live('click', function(event) {
      var target, inputs, hash;
      hash = { 0:24, 1:1.5, 2:2.5, 3:1.5, 4:1.5 };
      event.preventDefault();
      ended = false;
      target = $(event.target);
      inputs = $('input', target.parents('ul'));
      inputs.each(function(index, input) {
        var val, prev;
        input = $(input);
        if(input.val()) {
          val = parseFloat(input.val().replace(',', '.'));
          prev = val;
          inputs.slice(0, index).reverse().each(function(i, previous) {
            previous = $(previous);
            if(!previous.val()) {
              previous.val(prev / hash[index - (i+1)]);
            }
            prev = parseFloat(previous.val().replace(',', '.'));
          });
          prev = val;
          inputs.slice(index + 1).each(function(i, next) {
            next = $(next);
            if(!next.val()) {
              next.val(prev * hash[i + index]);
            }
            prev = parseFloat(next.val().replace(',', '.'));
          });
        }
      });
      
	
    });
    
    //slideshow for iPhone page
    jQuery(document).ready(function() {
        jQuery('#slideshow').cycle({ 
            delay:  3000, 
            speed:  800,
            pager: '#nav-slideshow'
        }); 

        function selectMarker() {
            /*jQuery('.slideshow_marker').removeClass('active_marker');
            jQuery('#slideshow_marker_' + this.alt).addClass('active_marker');*/
        };

    });
    
    //chosen
    $("#id_0-category-chosen").chosen();
    
});

function hideNotification() {
    $("#notification").slideUp("slow");
}
