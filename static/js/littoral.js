function handle_error(err) {
  if (err.code === 1) {
  	$('.select2-container').fadeToggle();
  }
}
$( window ).on("load", function() {
	if ( $('body').hasClass('index') ) {
	  if (navigator.geolocation) {
	    navigator.geolocation.getCurrentPosition(function(position) {
			var latitude = position.coords.latitude;
			var longitude = position.coords.longitude;
			$('#latitude').val(latitude);
			$('#longitude').val(longitude);
			$('#location').submit();
	    }, handle_error);
	  }
	  $('#station').select2({
	    placeholder: "Select a station"
	  });
	  $('#station').change(function () {
		var optionSelected = $('option:selected', this);
	    var valueSelected = optionSelected.val();
	    if ( valueSelected !== '' ) {
	      document.location.href = '/station/' + valueSelected;
	    }
	  });
	}
});