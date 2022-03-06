var showmap
var Thismarker

function showonmap(longitude, latitude, popuptext)
{	if (Thismarker)	showmap.removeLayer(Thismarker);
	Thismarker = L.marker([longitude, latitude]).addTo(showmap);
	showmap.panTo(new L.LatLng(longitude, latitude));
	window.location.href="#showmap";
	Thismarker.bindPopup(popuptext);
	Thismarker.openPopup();
}

function get_showmap()
{	showmap = L.map('showmap', { scrollWheelZoom: false }).setView([51.9467, 1.2879], 18);
	L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
	}).addTo(showmap);
	showmap.on('click', zoomToggle);
	function zoomToggle()
	{	if (showmap.scrollWheelZoom.enabled())
		{	showmap.scrollWheelZoom.disable();
		}
		else
		{   showmap.scrollWheelZoom.enable();
		}
	}
}

$(document).on('click', '#menu-button a', function() {
	if ($(this).text() == 'Menu') {
		console.log('Opening Menu...');
		$('.navlist').css('top','0px');
		$('.navlist').css('padding-bottom','20px');
		$('.navlist').css('padding-top','20px');
		$(this).text('Close Menu');
	} else {
		console.log('Closing Menu...');
		$('.navlist').css('top','-190px');
		$('.navlist').css('padding-bottom','0px');
		$('.navlist').css('padding-top','0px');
		$(this).text('Menu');
	}
});

// Expand/Contract <figure> width on clicking image... 
$(document).on('click', '.grower', function() {
	var ww = $(window).width();
	if (ww > 568) {
		targetDiv = $(this).parent(); // ie. the <figure>
		imgWidth = $(targetDiv).width() / $(targetDiv).parent().width() * 100;
		//console.log (imgWidth);
		if (imgWidth > 50) {
			targetDiv.css('width','46%');
		} else {
			targetDiv.css('width','100%');
		}
	}
});

function mailto(user, domain) { window.location = "mailto:" + user + "@" + domain; }