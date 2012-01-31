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
});
