
var map;
var markers;
var areas;

var current_construction_id = null;

$(document).ready(function() {
  close_sidebar();
  if ($('#map').exists()) {
    $('.scrollable-menu').css({'max-height': $( window ).height() - 74 });
    $('#menu-collapse').css({'max-height': $( window ).height() - 74 });
    $('.region').click(function(event) {
      event.preventDefault();
      region_id = $(this).data('regionid');
      map.setView(new L.LatLng(regions[region_id]['lat'], regions[region_id]['lon']), regions[region_id]['zoom']);
    });
    var ConstructionIcon = L.Icon.Default.extend({ options: { iconUrl: 'https://smartlane.io/baustellen/static/img/under_construction_icon.png', iconSize: [40, 35] } });
    constructionIcon = new ConstructionIcon();
    map = new L.Map('map', { attributionControl: false });
    var backgroundLayer = new L.TileLayer('https://otile1-s.mqcdn.com/tiles/1.0.0/map/{z}/{x}/{y}.jpg', {
      maxZoom: 18,
      minZoom: 4
    });
    L.control.attribution({ position: 'bottomleft', 'prefix': false }).addAttribution('Map Data &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Tiles courtesy of <a href="http://www.mapquest.com/" target="_blank">MapQuest</a>,  by <a href="http://leafletjs.com/">Leaflet</a>.'). addTo(map);
    map.setView(new L.LatLng(regions[0]['lat'], regions[0]['lon']), regions[0]['zoom']).addLayer(backgroundLayer);
    if ($('#flashes').exists())
      close_sidebar();
    get_construction_sites();
    
    map.on('moveend', function() {
      if (map.getZoom() > 10) {
        bounds = map.getBounds()
        $.getJSON('construction-area-list', {
          's': 2 * bounds.getSouth() - bounds.getNorth(),
          'w': 2 * bounds.getWest() - bounds.getEast(),
          'n': 2 * bounds.getNorth() - bounds.getSouth(),
          'e': 2 * bounds.getEast() - bounds.getWest()
        }).done(function(result) {
          if (!areas) {
            areas = new L.LayerGroup();
            areas.addTo(map);
          }
          else
            areas.clearLayers();
          $.each(result['response'], function(key, geojson) {
            if (geojson['area']['type'] == 'Polygon') {
              area = L.polyline(geojson['area']['coordinates'], {'color': '#FF3333', 'opacity': 1, 'fill': true})
              areas.addLayer(area);
            }
            else if (geojson['area']['type'] == 'MultiPolygon') {
              area = L.multiPolyline(geojson['area']['coordinates'], {'color': '#FF3333', 'opacity': 1, 'fill': true})
              areas.addLayer(area);
            }
            else if (geojson['area']['type'] == 'LineString') {
              area = L.polyline(geojson['area']['coordinates'], {'color': '#FF3333', 'opacity': 1});
              areas.addLayer(area);
            }
            else
              console.log('New GeoJSON detected');
          });
      });
      }
      else {
        if (areas)
          areas.clearLayers();
      }
    });
    
  }
});


function get_construction_sites() {
  $.getJSON('construction-list', function(result) {
    if (!markers) {
      markers = new L.MarkerClusterGroup({
        iconCreateFunction: function(cluster) {
          return new L.DivIcon({ html: '<strong>' + cluster.getChildCount() + '</strong>', iconSize: [40, 50] });
        }
      });
      markers.addTo(map);
    }
    else
      markers.clearLayers();
    $.each(result['response'], function(key, construction) {
      marker = L.marker([construction['lat'], construction['lng']], {icon: constructionIcon, title: construction.id});
      marker.on('click', function (current_marker) {
        if ($('#flashes').exists())
          $('#flashes').remove();
        current_marker_id = current_marker['target']['options']['title'];
        $.getJSON('construction-details?id=' + current_marker_id, function(result) {
          $("#details").animate({width:"290px"});
          construction = result['response'];
          current_construction_id = construction['id'];
          var html = '<span id="close-sidebar" onclick="close_sidebar();">schließen</span>';
          html += '<h2>Details</h2>';
          if (construction['begin'] || construction['end']) {
            html += '<h3>Zeitraum</h3><p>';
            if (construction['begin']) {
              html += '' + construction['begin'].substr(8, 2) + '.' + construction['begin'].substr(5, 2) + '.' + construction['begin'].substr(0, 4);
              if (construction['begin'].substr(11, 2) != '00')
                html += ', ' + construction['begin'].substr(11, 2) + ':' + construction['begin'].substr(14, 2);
            }
            else
              html += 'unbekannt';
            html += ' bis ';
            if (construction['end']) {
              html += construction['end'].substr(8, 2) + '.' + construction['end'].substr(5, 2) + '.' + construction['end'].substr(0, 4);
              if (!((construction['end'].substr(11, 2) == '23' && construction['end'].substr(14, 2) == '59') || (construction['end'].substr(11, 2) == '00' && construction['end'].substr(14, 2) == '00')))
                html += ', ' + construction['end'].substr(11, 2) + ':' + construction['end'].substr(14, 2);
              html += '</p>';
            }
            else
              html += 'unbekannt';
            html += '</p>';
          }
          if (construction['descr'] || construction['external_url']) {
            if (construction['descr'])
              html += '<h3>Beschreibung</h3><p>' + construction['descr'] + '</p>';
            if (construction['descr'] && construction['external_url'])
              html += ', ';
            if (construction['external_url'])
              html += '<a href=\"' + construction['external_url'] + '\">Weitere Informationen</a>';
          }
          if (construction['location_descr'])
            html += '<h3>Ort</h3><p>' + construction['location_descr'] + '</p>';
          if (construction['constructor'])
            html += '<h3>Bauherr</h3><p>' + construction['constructor'] + '</p>';
          if (construction['execution'])
            html += '<h3>Bauunternehmen</h3><p>' + construction['execution'] + '</p>';
          if (construction['restriction'])
            html += '<h3>Einschränkungen</h3><p>' + construction['restriction'] + '</p>';
          if (construction['licence_name']) {
            html += '<h3>Lizenz</h3><p>';
            if (construction['licence_url'])
              html += '<a href=\"' + construction['licence_url'] + '\">';
            html += construction['licence_name'];
            if (construction['licence_url'])
              html += '</a>';
            if (construction['licence_owner'])
              html += ', Datenquelle: ' + construction['licence_owner'];
            html += '</p>';
          }
          $('#details').html(html);
        });
      });
      markers.addLayer(marker);
    });
  });
}

function close_sidebar() {
  $("#details").html('');
  $("#details").animate({width:"0px", 'padding-left': '0px', 'padding-right': '0px'});
}

function filterGeocodingChoices(results) {
  results = deepCopy(results);
  // Alle Einträge bekommen eigenen Qualitäts-Koeffizienten
  for (var n in results) {
    results[n].okquality = 1.0;
    // verdreifache wenn neighborhood gesetzt
    if (results[n].address.suburb != '') {
      results[n].okquality *= 3.0;
    }
    // verdopple wenn PLZ gesetzt
    if (results[n].address.postcode != '') {
      results[n].okquality *= 3.0;
    }
    // keine Straße gesetzt: Punktzahl durch 10
    if (typeof(results[n].address.road) === 'undefined') {
        results[n].okquality *= 0.1;
    }
  }
  // Sortieren nach 'okquality' abwärts
  results.sort(qualitySort);
  var resultByPostCode = {};
  var n;
  for (n in results) {
    if (typeof(resultByPostCode[results[n].address.postcode]) === 'undefined') {
      resultByPostCode[results[n].address.postcode] = results[n];
    }
  }
  ret = [];
  for (n in resultByPostCode) {
    ret.push(resultByPostCode[n]);
  }
  // Sortieren nach Längengrad
  ret.sort(longitudeSort);
  return ret;
}

function longitudeSort(a, b) {
  return parseFloat(a.lon) - parseFloat(b.lon)
}

function qualitySort(a, b) {
  return b.okquality - a.okquality
}

function deepCopy(obj) {
  if (typeof obj !== "object") return obj;
  if (obj.constructor === RegExp) return obj;
  
  var retVal = new obj.constructor();
  for (var key in obj) {
    if (!obj.hasOwnProperty(key)) continue;
    retVal[key] = deepCopy(obj[key]);
  }
  return retVal;
}

jQuery.fn.exists = function(){return this.length>0;}
