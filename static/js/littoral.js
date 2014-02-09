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
});