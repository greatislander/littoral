function handle_error(err) {
  if (err.code === 1) {
    // user denied access to location
	$('.location').remove();
  }
}
$( window ).load(function() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
		var latitude = position.coords.latitude;
		var longitude = position.coords.longitude;
		$('.location').text(latitude + ',' + longitude);
    }, handle_error);
  }
  $('#station').chosen({allow_single_deselect: true});
  $('#station').change(function () {
	var optionSelected = $('option:selected', this);
    var valueSelected = optionSelected.val();
    if ( valueSelected !== '' ) {
      document.location.href = '/station/' + valueSelected;
    }
  });
});