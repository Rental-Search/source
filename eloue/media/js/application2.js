$(document).ready(function() {
    /*Display home tabs */
    $( ".products-home-tabs" ).tabs();
    
    /* Display city input to change the localisation */
    $('.btn-other-town').click(function () {
        $('.search-home').addClass('editing');
    });
    
    /* Display the city input */
    $('.btn-edit-town').click(function () {
        $('.search-home').removeClass('editing');
    });
    $('.btn-cancel-edit-town').click(function () {
        $('.search-home').removeClass('editing');
    });
    
    /*Display product detail tabs */
    $( ".product-tabs" ).tabs();
    
    
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
