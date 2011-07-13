$(document).ready(function() {
    
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
});

function hideNotification() {
    $("#notification").slideUp("slow");
}