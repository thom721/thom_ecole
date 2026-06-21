<template>
    <AppLayout1 title="Dashboard">
        <div class="h-screen w-full">
            <div ref="mapContainer" class="h-full w-full"></div>
        </div>
    </AppLayout1>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ref as dbRef, onValue } from 'firebase/database';
import AppLayout1 from '@/Layouts/AppLayout1.vue';
import { database } from '@/firebase_';

// const mapContainer = ref(null);
// const rides = ref({});
// let map = null;
// let directionsService = null;
// let directionsRenderers = {};

// onMounted(async () => {
//     await loadGoogleMaps();
//     initMap();
//     setupFirebaseListener();
// });

// function loadGoogleMaps() {
//     return new Promise((resolve) => {
//         if (window.google && window.google.maps) {
//             resolve();
//             return;
//         }

//         const script = document.createElement('script');
//         script.src = `https://maps.googleapis.com/maps/api/js?key=AIzaSyAJvEbIp3nL8XGLuDpYY8tZMaav905NAHE&libraries=directions`;
//         script.async = true;
//         script.defer = true;
//         script.onload = resolve;
//         document.head.appendChild(script);
//     });
// }

// function initMap() {
//     map = new google.maps.Map(mapContainer.value, {
//         center: { lat: 48.8566, lng: 2.3522 },
//         zoom: 13,
//         disableDefaultUI: true,
//         styles: [
//             {
//                 featureType: "poi",
//                 stylers: [{ visibility: "on" }]
//             }
//         ]
//     });

//     directionsService = new google.maps.DirectionsService();
// }

// function setupFirebaseListener() {
//     const ridesRef = dbRef(database, 'rides');

//     onValue(ridesRef, (snapshot) => {
//         rides.value = snapshot.val() || {};
//         renderAllRoutes();
//     });
// }

// function renderAllRoutes() {
//     clearAllRoutes();

//     Object.entries(rides.value).forEach(([id, ride]) => {
//         renderRoute(
//             ride.pickupLocation.lat,
//             ride.pickupLocation.lng,
//             ride.destination.lat,
//             ride.destination.lng,
//             id
//         );
//     });
// }

// function renderRoute(startLat, startLng, endLat, endLng, rideId) {
//     directionsService.route({
//         origin: { lat: startLat, lng: startLng },
//         destination: { lat: endLat, lng: endLng },
//         travelMode: google.maps.TravelMode.DRIVING
//     }, (response, status) => {
//         if (status === 'OK') {
//             directionsRenderers[rideId] = new google.maps.DirectionsRenderer({
//                 map,
//                 directions: response,
//                 suppressMarkers: false,
//                 polylineOptions: {
//                     strokeColor: "#4285F4",
//                     strokeOpacity: 0.7,
//                     strokeWeight: 5
//                 },
//                 markerOptions: {
//                     icon: {
//                         path: google.maps.SymbolPath.CIRCLE,
//                         scale: 8,
//                         fillColor: "#000",
//                         fillOpacity: 1,
//                         strokeWeight: 2,
//                         strokeColor: "white"
//                     }
//                 }
//             });
//         }
//     });
// }

// function clearAllRoutes() {
//     Object.values(directionsRenderers).forEach(renderer => {
//         renderer.setMap(null);
//     });
//     directionsRenderers = {};
// }

const mapContainer = ref(null);
const rides = ref({});
let map = null;
let directionsService = null;
let directionsRenderers = {};
let markers = {}; // Pour stocker les marqueurs personnalisés

onMounted(async () => {
    await loadGoogleMaps();
    initMap();
    setupFirebaseListener();
});

function loadGoogleMaps() {
    return new Promise((resolve) => {
        if (window.google && window.google.maps) {
            resolve();
            return;
        }

        const script = document.createElement('script');
        script.src = `https://maps.googleapis.com/maps/api/js?key=AIzaSyAJvEbIp3nL8XGLuDpYY8tZMaav905NAHE&libraries=directions`;
        script.async = true;
        script.defer = true;
        script.onload = resolve;
        document.head.appendChild(script);
    });
}

function initMap() {
    map = new google.maps.Map(mapContainer.value, {
        center: { lat: 48.8566, lng: 2.3522 },
        zoom: 13,
        disableDefaultUI: true,
        styles: [
            {
                featureType: "poi",
                stylers: [{ visibility: "on" }]
            }
        ]
    });

    directionsService = new google.maps.DirectionsService();
}

function setupFirebaseListener() {
    const ridesRef = dbRef(database, 'rides');

    onValue(ridesRef, (snapshot) => {
        rides.value = snapshot.val() || {};
        renderAllRoutes();
    });
}

function renderAllRoutes() {
    clearAllRoutes();

    Object.entries(rides.value).forEach(([id, ride]) => {
        renderRoute(
            ride.pickupLocation.lat,
            ride.pickupLocation.lng,
            ride.destination.lat,
            ride.destination.lng,
            id
        );
    });
}

function renderRoute111(startLat, startLng, endLat, endLng, rideId) {
    directionsService.route({
        origin: { lat: startLat, lng: startLng },
        destination: { lat: endLat, lng: endLng },
        travelMode: google.maps.TravelMode.DRIVING
    }, (response, status) => {
        if (status === 'OK') {
            // Création du rendu de la route
            directionsRenderers[rideId] = new google.maps.DirectionsRenderer({
                map,
                directions: response,
                suppressMarkers: true, // On masque les marqueurs par défaut
                polylineOptions: {
                    strokeColor: "#4285F4",
                    strokeOpacity: 0.7,
                    strokeWeight: 5
                }
            });

            // Stockage des marqueurs personnalisés
            markers[rideId] = {
                start: createMarker(
                    response.routes[0].legs[0].start_location,
                    "#34D399", // Vert pour le départ
                    "Départ"
                ),
                end: createMarker(
                    response.routes[0].legs[0].end_location,
                    "#EF4444", // Rouge pour l'arrivée
                    "Arrivée"
                )
            };
        }
    });
}

function renderRoute(startLat, startLng, endLat, endLng, rideId) {
    directionsService.route({
        origin: { lat: startLat, lng: startLng },
        destination: { lat: endLat, lng: endLng },
        travelMode: google.maps.TravelMode.DRIVING
    }, (response, status) => {
        if (status === 'OK') {
            directionsRenderers[rideId] = new google.maps.DirectionsRenderer({
                map,
                directions: response,
                suppressMarkers: true,
                polylineOptions: {
                    strokeColor: "#122a55",
                    strokeOpacity: 1,
                    strokeWeight: 4
                }
            });

            // Marqueur de départ
            markers[rideId] = {
                start: createMarker(response.routes[0].legs[0].start_location, {
                    icon: '<path d="M17.0839 15.812C19.6827 13.0691 19.6379 8.73845 16.9497 6.05025C14.2161 3.31658 9.78392 3.31658 7.05025 6.05025C4.36205 8.73845 4.31734 13.0691 6.91612 15.812C7.97763 14.1228 9.8577 13 12 13C14.1423 13 16.0224 14.1228 17.0839 15.812ZM12 23.7279L5.63604 17.364C2.12132 13.8492 2.12132 8.15076 5.63604 4.63604C9.15076 1.12132 14.8492 1.12132 18.364 4.63604C21.8787 8.15076 21.8787 13.8492 18.364 17.364L12 23.7279ZM12 12C10.3431 12 9 10.6569 9 9C9 7.34315 10.3431 6 12 6C13.6569 6 15 7.34315 15 9C15 10.6569 13.6569 12 12 12Z"></path>',
                    color: 'rgb(77, 140, 63)', // Vert
                    title: 'Point de départ',
                    bgColor: 'red'
                }),

                // Marqueur d'arrivée
                end: createMarker(response.routes[0].legs[0].end_location, {
                    icon: '<path fill="none" d="M0 0h24v24H0z"></path><path d="M3 3H12.382C12.7607 3 13.107 3.214 13.2764 3.55279L14 5H20C20.5523 5 21 5.44772 21 6V17C21 17.5523 20.5523 18 20 18H13.618C13.2393 18 12.893 17.786 12.7236 17.4472L12 16H5V22H3V3Z"></path>',
                    color: 'rgb(234, 67, 49)', // Rouge
                    title: 'Point d\'arrivée',
                    bgColor: 'blue'
                })
            };
        }
    });
}

function createMarker(position, iconConfig) {
    // Configuration par défaut
    const defaults = {
        icon: '<path d="M17.0839 15.812C19.6827 13.0691 19.6379 8.73845 16.9497 6.05025C14.2161 3.31658 9.78392 3.31658 7.05025 6.05025C4.36205 8.73845 4.31734 13.0691 6.91612 15.812C7.97763 14.1228 9.8577 13 12 13C14.1423 13 16.0224 14.1228 17.0839 15.812ZM12 23.7279L5.63604 17.364C2.12132 13.8492 2.12132 8.15076 5.63604 4.63604C9.15076 1.12132 14.8492 1.12132 18.364 4.63604C21.8787 8.15076 21.8787 13.8492 18.364 17.364L12 23.7279ZM12 12C10.3431 12 9 10.6569 9 9C9 7.34315 10.3431 6 12 6C13.6569 6 15 7.34315 15 9C15 10.6569 13.6569 12 12 12Z"></path>', // Classe de base RemixIcon
        color: 'rgba(54,201,107,1)',        // Couleur rouge par défaut
        size: 36,                // Taille en pixels
        title: '',               // Texte de l'infobulle
        bgColor: 'red',        // Couleur de fond
        shadow: true             // Ajouter une ombre
    };

    const config = { ...defaults, ...iconConfig };

    // Création du SVG personnalisé

    const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="36" height="36" fill="${config.color}"><path fill="none" d="M0 0h24v24H0z"></path>${config.icon}</svg>
    `;

    return new google.maps.Marker({
        position,
        map,
        title: config.title,
        icon: {
            url: 'data:image/svg+xml;charset=UTF-8;base64,' + btoa(unescape(encodeURIComponent(svg))),
            scaledSize: new google.maps.Size(config.size, config.size),
            anchor: new google.maps.Point(config.size / 2, config.size)
        },
        optimized: false
    });
}

// Helper pour obtenir le caractère Unicode de l'icône
function getIconChar(iconClass) {
    // Mapping des icônes RemixIcon courantes
    const iconMap = {
        'ri-map-pin-3-fill': '&#xefae;',
        'ri-map-pin-fill': '&#xefaf;',
        'ri-flag-line': '&#xee4f;',
        'ri-flag-fill': '&#xee50;',
        'ri-car-line': '&#xec49;',
        'ri-car-fill': '&#xec4a;',
        'ri-user-location-line': '&#xf1b3;',
        'ri-user-location-fill': '&#xf1b4;'
    };

    return iconMap[iconClass] || '&#xefae;'; // Par défaut: map-pin
}

// function createMarker(position, color, title,icon=icon) {
//     return new google.maps.Marker({
//         position,
//         map,
//         title,
//         icon: {
//             path: google.maps.SymbolPath.CIRCLE,
//             scale: 8,
//             fillColor: color,
//             fillOpacity: 1,
//             strokeWeight: 2,
//             strokeColor: "white"
//         }
//     });
// }

function clearAllRoutes() {
    // Nettoyer les rendus de routes
    Object.values(directionsRenderers).forEach(renderer => {
        renderer.setMap(null);
    });
    directionsRenderers = {};

    // Nettoyer les marqueurs
    Object.values(markers).forEach(markerGroup => {
        markerGroup.start.setMap(null);
        markerGroup.end.setMap(null);
    });
    markers = {};
}
</script>