initMap = ->
	map = new google.maps.Map $('#map')[0], {
		center: {lat: 41.618460, lng: -83.617682},
		zoom: 12
	}
	autocomplete = new google.maps.places.Autocomplete $('#search-box')[0]
	return
