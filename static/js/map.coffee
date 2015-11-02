markers = []
place_cache = null

isExactLocation = (place) ->
	addr_types = [
		'street_address'
		'intersection'
		'premise'
		'subpremise'
		'natural_feature'
		'airport'
		'park'
		'point_of_interest'
	]
	return addr_types.some (c, i, a) ->
		return place.types.indexOf(c) != -1

initMap = ->
	map = new google.maps.Map $('#map')[0], {
		center: {lat: 41.618460, lng: -83.617682}
		zoom: 10
		componentRestrictions: {country: 'us'}
	}
	autocomplete = new google.maps.places.Autocomplete $('#search-box')[0]
	autocomplete.addListener 'place_changed', ->
		p = autocomplete.getPlace()
		if isExactLocation(p)
			map.setZoom 14
		else
			map.setZoom 10
		plotNearby p
		place_cache = p

	plotNearby = (place) ->
		for m in markers
			m.setMap null
		markers = []
		loc = place.geometry.location
		map.setCenter loc
		$.get '/nearby', {lng: loc.lng(), lat: loc.lat(), radius: $('#radius-select').val()}, (data) ->
			for x in data
				if x.score < 60
					color = 'red'
				else if x.score < 80
					color = 'yellow'
				else
					color = 'green'
				marker = new google.maps.Marker {
					position: {
						lng: x.geo.coordinates[0]
						lat: x.geo.coordinates[1]
					}
					icon: "http://maps.google.com/mapfiles/ms/icons/#{ color }-dot.png"
					map: map
				}
				la =JSON.parse x.location[0]
				iwc = "<p><b>#{ x['hospital name'] }</b></p>
						<ul>
							<li>Score: #{ +x.score.toFixed(2) }</li>
							<li>Rank: #{ x.rank } / 4300</li>
							<li>#{ la.address }, #{ la.city }, #{ la.state } #{ la.zip }</li>
							<li>Phone: <a href=\"tel:#{ x['phone number'][0] }\">#{ x['phone number'][0] }</a></li>
						</ul>
				"
				markers.push marker
				attachInfoWindow marker, iwc
						
	attachInfoWindow = (marker, content) ->
		marker.addListener 'click', ->
			iw = new google.maps.InfoWindow {
				content: content
			} 
			iw.open(map, marker)
	
	$('#radius-select').change ->
		if place_cache?
			plotNearby place_cache
		
