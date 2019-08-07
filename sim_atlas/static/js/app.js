function load_map() {
    map = L.map('mapid').setView([-41.2728, 173.2995], 5);
    L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
        maxZoom: 18,
        id: 'mapbox.streets',
        accessToken: 'pk.eyJ1IjoiLXZpa3Rvci0iLCJhIjoiY2pzam9mNXVoMm9xdzQ0b2FmNnNqODE4NCJ9.AnNONHzKRb5vdl2Ikw2l2Q'
    }).addTo(map);
}

function load_polylines() {
    $.getJSON("../static/data/fault_traces.json", function (json) {
        console.log(json);
        map_faults = L.layerGroup();
        map_faults.clearLayers();
        var popup = L.popup();
        for (var i = 0; i < json.length; i++) {
            (function () {
                var d = json[i];
                console.log(d.traces);

                map_faults.addLayer(L.polyline(d.traces, {
                        color: "red",
                        opacity: 0.5,
                        weight: 2
                    })
                        .bindPopup(popup)
                        .on("mouseover", function (e) {
                            e.target.setStyle({
                                color: "blue",
                                opacity: 1,
                                weight: 5
                            });
                            e.target.getPopup().setLatLng(e.latlng).openOn(map);
                            e.target.getPopup().setContent(d.name + '</br><a href=' + d.video + '> Simulation Video </a>');
                        })
                        .on("mouseout", function (e) {
                            e.target.setStyle({
                                color: "red",
                                opacity: 0.5,
                                weight: 2
                            });
//                            e.target.closePopup();
                        })
                        .on("click", function (e) {
                            e.target.getPopup().setLatLng(e.latlng).openOn(map);
                            e.target.getPopup().setContent(d.name + '</br><a href=' + d.video + '> Simulation Video </a>');
                        })
                );
            })();
        }
        map_faults.addTo(map);
    });
}


$(document).ready(function ()
{
    load_map();
    load_polylines();
});
