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

function SuccessBuilder(priority, forced, geocodeSuccess) {
    return function(position) {
        geocoder = new google.maps.Geocoder();
        latlon = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
        geocoder.geocode(
            {'latLng':latlon},
            function(result) {
                report_location_back(priority, forced, result[0], latlon, geocodeSuccess);
            }
        );
    };
}

function geocoder_error_handler(error) {
    $.cookie('geocoding', 'failed', { expires: 1, path: '/' });
}

function report_location_back(source, forced, address, coords, success) {
  $(document).ajaxSend(function(event, xhr, settings) {
    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
  });
  $.ajax({
    type: 'POST',
    url: '/user_geolocation/',
    data: {
      address: JSON.stringify(address),
      coordinates: JSON.stringify({
        lat: coords.lat(),
        lon: coords.lng()
      }),
      source: source,
      forced: forced
    },
    success: function(response) {
        if (response["status"] == "OK") {
            $.cookie('geocoding', 'success', { expires: 1, path: '/' });
            success();
        }
    }
  });
}

geolocation_stuff = function() {
    autocomplete = new google.maps.places.Autocomplete(
        document.getElementById("id_l"), 
        {
            types: ['geocode'], 
            bounds: new google.maps.LatLngBounds(
                new google.maps.LatLng(42.13316390, -5.982051999999999), 
                new google.maps.LatLng(50.03800220, 10.409550)
            )
        }
    );

    google.maps.event.addListener(autocomplete, 'place_changed', function() {
      place = autocomplete.getPlace();
      report_location_back(1, true, place, place.geometry.location, function() {window.location.reload();});
    });

    $("#rayon_update").click(function() {
        $(document).ajaxSend(function(event, xhr, settings) {
            if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        });
        $.ajax({
            type: 'POST',
            url: '/user_geolocation/',
            data: {
                source: 1,
                radius: $("#id_r").val().replace(RegExp(',', 'g'), '.'),
                forced: true
            },
            success: function(response) {
                if (response["status"] == "OK") {
                    $("#form_search_results").submit();
                }
            }
        });
    });
}

$(document).ready(function() {
    var isProfessionalInput, 
        companyNameInput,
        productHomeTab,
        btnOtherTown,
        btnEditTown,
        btnCancelEditTown,
        productTab,
        workInput,
        schoolInput,
        languagesInput,
        bookingCreate,
        startDate,
        endDate,
        moreItem


    // Company name field display/none
    isProfessionalInput = $("input[name*='is_professional']");
    companyNameInput = $("input[name*='company_name']");
    companyNameInput.parent().parent().hide();

    var exists = $("input[name*='is_professional']:checked").val();

    if (exists == 'on') {
        companyNameInput.parent().parent().show();
    }
    $(":checkbox").click(function() {
        if (isProfessionalInput.is(':checked')) {
            companyNameInput.parent().parent().show();
        } else {
            companyNameInput.parent().parent().hide();
        }
    });


    //Display home tabs
    productHomeTab = $( ".products-home-tabs" );
    productHomeTab.tabs();
    
    //Display city input to change the localisation
    btnOtherTown = $('.btn-other-town');
    btnOtherTown.click(function () {
        $('.search-home').addClass('editing');
    });

    //Display the city input
    btnEditTown = $('.btn-edit-town');
    btnEditTown.click(function () {
        navigator.geolocation.getCurrentPosition(
            SuccessBuilder(2, true, function(){window.location.reload();}), 
            geocoder_error_handler
        );
    });

    btnCancelEditTown = $('.btn-cancel-edit-town');
    btnCancelEditTown.click(function () {
        $('.search-home').removeClass('editing');
    });
    
    //Display product detail tabs
    btnCancelEditTown = $( ".product-tabs" );
    btnCancelEditTown.tabs();

    workInput = $("#id_moreInfoEdit-work");
    workInput.autocomplete(
        {
            'source': function(request, response) {
                $.getJSON('accounts_work_autocomplete'+'?term='+request.term, response);}
        }
    );
    schoolInput = $("#id_moreInfoEdit-school");
    schoolInput.autocomplete(
        {
            'source': function(request, response) {
                $.getJSON('accounts_studies_autocomplete'+'?term='+request.term, response);}
        }
    );
    languagesInput = $("#id_languages");
    languagesInput.chosen();
    
    // Booking price
    // Price calculations
    bookingPrice = function(form) {
        var template,
        serializedForm;
        availabilityTemplate = '{{^errors}}<p class="available">Ces dates sont disponibles</p>{{/errors}}{{#errors}}<p class="unavailable">Ces dates ne sont pas disponibles</p>{{/errors}}'
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
                $("#available").html(Mustache.to_html(availabilityTemplate, data));
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
    
    bookingCreate.change(function(event) {
        bookingPrice($(this));
    });
    
    //Display datepicker on product detail page
    startDate = $('input[name$=started_at_0]');
    startDate.datepicker({
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
    
    endDate = $('input[name$=ended_at_0]');
    endDate.datepicker({
        dateFormat: 'dd/mm/yy',
    });

    //fbconnect
    $('#fbconnect').click(function () {
        FB.login(function(response) {
           if (response.authResponse) {
             $('input[name$="facebook_access_token"]').val(response.authResponse.accessToken);
             $('input[name$="facebook_expires"]').val(response.authResponse.expiresIn);
             $('input[name$="facebook_uid"]').val(response.authResponse.userID);
             $('input[name$="email"]').removeAttr('value');
             $('input[name$="password"]').removeAttr('value');
           }
           $('form').submit();
           $('input[type="submit"]').attr('disabled','disabled');
           $('#fbconnect').remove();
           $('.fbconnect-content .fb-slogan').html('Connexion en cours...');
         }, {scope: 'email,user_location'});
    });
});
