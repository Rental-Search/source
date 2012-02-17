function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
function sameOrigin(url) {
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}
function safeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function SuccessBuilder(priority, geocodeSuccess) {
    return function(position) {
        geocoder = new google.maps.Geocoder();
        latlon = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
        geocoder.geocode(
            {'latLng':latlon}, 
            function(result) {
                report_location_back(priority, result[0], latlon, function(response) {
                    if (response["status"] == "OK") {
                        geocodeSuccess();
                    }
                });
            }
        );
    };
}

function report_location_back(source, address, coords, success) {
  success = (typeof success == "undefined")?function(response) {

      if (response["status"] == 'OK') {
        window.location.reload();
      }
    }:success;
  $(document).ajaxSend(function(event, xhr, settings) {
    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
  });
  $.ajax({
    type: 'POST',
    url: document.location.origin+'/user_geolocation/',
    data: {
      address: JSON.stringify(address),
      coordinates: JSON.stringify({
        lat: coords.lat(),
        lon: coords.lng()
      }),
      source: source
    },
    success: success
  });
}

$(document).ready(function() {
    /*Display home tabs */
    $( ".products-home-tabs" ).tabs();
    
    /* Display city input to change the localisation */
    $('.btn-other-town').click(function () {
        $('.search-home').addClass('editing');
    });

    /* Display the city input */
    $('.btn-edit-town').click(function () {
        navigator.geolocation.getCurrentPosition(SuccessBuilder(1, function(){window.location.reload();}));
    });
    $('.btn-cancel-edit-town').click(function () {
        $('.search-home').removeClass('editing');
    });
    
    /*Display product detail tabs */
    $( ".product-tabs" ).tabs();
    

    $("#id_work").autocomplete(
        {
            'source': function(request, response) {
                $.getJSON('accounts_work_autocomplete'+'?term='+request.term, response);}
        }
    );
    $("#id_school").autocomplete(
        {
            'source': function(request, response) {
                $.getJSON('accounts_studies_autocomplete'+'?term='+request.term, response);}
        }
    );
    
    $("#id_languages").chosen();

    
    /* Booking price */
    // Price calculations
    bookingPrice = function(form) {
        var template,
        serializedForm;
        unitTemplate = '<span class="price">{{unit_value}}</span><span class="unit"> / par {{unit_name}}</span>';
        priceTemplate = '{{#warnings}}{{ warnings }}{{/warnings}} {{#errors}}{{ errors }}{{/errors}}{{^errors}}Total :<span class="day">{{ duration }},</span> soit <span class="pricing">{{ total_price }}</span>{{/errors}}';
        listTemplate = '{{#select_list}}<option value="{{value}}" {{#selected}}selected="selected"{{/selected}}>{{value}}</option>{{/select_list}}';
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
                $("#product_price").html(Mustache.to_html(unitTemplate, data));
                $("#booking-total").html(Mustache.to_html(priceTemplate, data));
                $("#id_0-quantity").html(Mustache.to_html(listTemplate, data));
            }
        });
    }
    bookingCreate = $('#booking_create');
    if (bookingCreate.length > 0) {
        bookingPrice(bookingCreate);
    }
    
    $('#booking_create').change(function(event) {
        bookingPrice($(this));
    });
    
    //Display datepicker on product detail page
    $('input[name$=started_at_0]').datepicker({
        dateFormat: 'dd/mm/yy',
        minDate: 1,
        maxDate: '+360d',
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
    });
});
