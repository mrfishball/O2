$(document).ready(function() {
	// Allow alert banners to automatically dismiss with a slide up animation.
	$(".alert").fadeTo(4500, 200).slideUp(200, function(){
    	$(".alert").alert('close');
	});

	$(function(){
	  /* Scroll to top */
	  $(window).scroll(function(){
	    ( $(this).scrollTop() > 300 ) ? $("a#scroll-to-top").addClass('visible') : $("a#scroll-to-top").removeClass('visible');
	  });
	  $("a#scroll-to-top").click(function() {
	    $("html, body").animate({ scrollTop: 0 }, "slow");
	    return false;
	  });

	});
	
});

