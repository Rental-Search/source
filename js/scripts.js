$( document ).ready( function() {
	$( ".product-list" ).find( '.product-item:nth-of-type(4n)' ).css( "margin-right", "0" );
	console.log( $( ".product-list" ).find( '.products-item:nth-of-type(4n)' ));
} );