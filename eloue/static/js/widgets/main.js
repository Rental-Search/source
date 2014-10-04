require.config({
    baseUrl: "/static/js/widgets",
    paths: {
        "bootstrap": "/static/bower_components/bootstrap/dist/js/bootstrap.min",
        "lodash": "/static/bower_components/lodash/dist/lodash.min",
        "jQuery": "/static/bower_components/jquery/dist/jquery.min",
        "jquery-ui": "/static/bower_components/jqueryui/jquery-ui.min",
        "slider": "/static/bower_components/jqueryui/ui/minified/slider.min",
        "core": "/static/bower_components/jqueryui/ui/minified/core.min",
        "mouse": "/static/bower_components/jqueryui/ui/minified/mouse.min",
        "widget": "/static/bower_components/jqueryui/ui/minified/widget.min",
        "angular": "/static/bower_components/angular/angular.min",
        "angular-resource": "/static/bower_components/angular-resource/angular-resource.min",
        "angular-route": "/static/bower_components/angular-route/angular-route.min",
        "angular-cookies": "/static/bower_components/angular-cookies/angular-cookies.min",
        "angular-sanitize": "/static/bower_components/angular-sanitize/angular-sanitize.min",
        "moment": "/static/bower_components/moment/min/moment.min",
        "angular-moment": "/static/bower_components/angular-moment/angular-moment.min",
        "bootstrap-datepicker": "/static/bower_components/bootstrap-datepicker/js/bootstrap-datepicker",
        "bootstrap-datepicker-fr": "/static/bower_components/bootstrap-datepicker/js/locales/bootstrap-datepicker.fr",
        "jquery-form": "/static/bower_components/jquery-form/jquery.form",
        "datejs": "/static/bower_components/datejs/build/production/date.min",
        "chosen": "/static/bower_components/chosen/chosen.jquery.min",
        "html5shiv": "/static/bower_components/html5shiv/dist/html5shiv.min",
        "respond": "/static/bower_components/respond/respond.min",
        "placeholders-utils": "/static/bower_components/placeholders/lib/utils",
        "placeholders-main": "/static/bower_components/placeholders/lib/main",
        "placeholders-jquery": "/static/bower_components/placeholders/lib/adapters/placeholders.jquery",
        "custom-scrollbar": "/static/bower_components/malihu-custom-scrollbar-plugin/jquery.mCustomScrollbar",
        "jquery-mousewheel": "/static/bower_components/jquery-mousewheel/jquery.mousewheel",
        "toastr": "/static/bower_components/toastr/toastr.min",
        "formmapper": "/static/js/formmapper"
    },
    shim: {
        "angular": {"exports": "angular"},
        "angular-route": ["angular"],
        "angular-cookies": ["angular"],
        "angular-sanitize": ["angular"],
        "angular-resource": ["angular"],
        "angular-moment": ["angular"],
        "angular-mocks": {
            deps: ["angular"],
            "exports": "angular.mock"
        },
        "jQuery": {exports: "jQuery"},
        "jquery-ui": ["jQuery"],
        "slider": ["jQuery"],
        "core": ["jQuery"],
        "mouse": ["jQuery"],
        "widget": ["jQuery"],
        "bootstrap": ["jQuery"],
        "jquery-form": ["jQuery"],
        "moment": ["jQuery"],
        "bootstrap-datepicker": ["jQuery"],
        "bootstrap-datepicker-fr": ["jQuery", "bootstrap-datepicker"],
        "chosen": ["jQuery"],
        "placeholders-jquery": ["jQuery"],
        "formmapper": ["jQuery"],
        "jquery-mousewheel": ["jQuery"],
        "custom-scrollbar": ["jQuery", "jquery-mousewheel"],
        "toastr": ["jQuery"]
    }
});

require([
    "jQuery",
    "lodash",
    "angular",
    "bootstrap",
    "moment",
    "angular-moment",
    "datejs",
    "chosen",
    "html5shiv",
    "respond",
    "placeholders-utils",
    "placeholders-main",
    "placeholders-jquery",
    "formmapper",
    "toastr",
    "jquery-form",
//    "jquery-ui",
    "slider",
    "core",
    "mouse",
    "widget",
    "bootstrap-datepicker",
    "bootstrap-datepicker-fr",
    "eloue/route"
], function ($, _, angular) {
    "use strict";
    $(function () {
        $("select").attr("eloue-chosen", "");

        angular.bootstrap(document, ["EloueApp"]);

        var slide_imgs = [].slice.call($('.carousel-wrapper').find('img'));
        for (var index = 0; index < slide_imgs.length; index++) {
            var proportions = $(slide_imgs[index]).width() / $(slide_imgs[index]).height(),
                parent = $(slide_imgs[index]).parent(),
                parent_proportions = $(parent).width() / $(parent).height();

            if (proportions < parent_proportions) {
                $(slide_imgs[index]).addClass('expand-v');
            } else {
                $(slide_imgs[index]).addClass('expand-h');
            }
        }

        var layout_switcher = $('.layout-switcher'), article = $('article');
        if (layout_switcher && article) {
            // switch grid/list layouts
            $(layout_switcher).on('click', 'i', function () {
                if ($(this).hasClass('grid')) {
                    article.removeClass('list-layout');
                    article.addClass('grid-layout')
                } else {
                    article.removeClass('grid-layout');
                    article.addClass('list-layout')

                }
            });
        }

        var districtFake = $("#district-fake"), priceFake = $("#price-fake");
        if (districtFake) {
            districtFake.slider({
                range: "min",
                value: 400,
                min: 1,
                max: 700
            });
        }

        if (priceFake) {
            priceFake.slider({
                range: true,
                min: 0,
                max: 700,
                values: [100, 400]
            });
        }

        (function (d, s, id) {
            var js, fjs = d.getElementsByTagName(s)[0];
            if (d.getElementById(id)) return;
            js = d.createElement(s);
            js.id = id;
            js.src = "//connect.facebook.net/en_US/sdk.js#xfbml=1&version=v2.0";
            fjs.parentNode.insertBefore(js, fjs);
        }(document, 'script', 'facebook-jssdk'));

        window.___gcfg = {lang: 'fr'};
        (function () {
            var po = document.createElement('script');
            po.type = 'text/javascript';
            po.async = true;
            po.src = 'https://apis.google.com/js/platform.js';
            var s = document.getElementsByTagName('script')[0];
            s.parentNode.insertBefore(po, s);
        })();

        !function (d, s, id) {
            var js, fjs = d.getElementsByTagName(s)[0], p = /^http:/.test(d.location) ? 'http' : 'https';
            if (!d.getElementById(id)) {
                js = d.createElement(s);
                js.id = id;
                js.src = p + '://platform.twitter.com/widgets.js';
                fjs.parentNode.insertBefore(js, fjs);
            }
        }(document, 'script', 'twitter-wjs');

        // Insert YouTube video into defined container, add play on modal open and stop on modal hide
        var tag = document.createElement('script');

        tag.src = "https://www.youtube.com/iframe_api";
        var firstScriptTag = document.getElementsByTagName('script')[0];
        firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
        var videoModal = $('#videoModal');
        var player;

        videoModal.on('shown.bs.modal', function () {
            player = new YT.Player('videoContainer', {
                height: '480',
                width: '640',
                videoId: 'nERu_2pSSb0',
                events: {
                    'onReady': onPlayerReady
                }
            });
        });
        videoModal.on('hidden.bs.modal', function () {
            player.destroy();
        });

        function onPlayerReady(event) {
            event.target.playVideo();
        }


        window.google_maps_loaded = function () {
            $('#geolocate').formmapper({
                details: "form"
            });

            var mapCanvas = document.getElementById("map-canvas");

            if (!!mapCanvas) {


                var radius = Number($("#district").val().replace(',', '.'));

                var mapOptions = {
                    zoom: zoom(radius),
                    disableDefaultUI: true,
                    zoomControl: true,
                    mapTypeId: google.maps.MapTypeId.ROADMAP
                };
                var map = new google.maps.Map(mapCanvas, mapOptions);
                var geocoder = new google.maps.Geocoder();
                geocoder.geocode(
                    {address: document.getElementById("where").value},
                    function (result, status) {
                        if (status == google.maps.GeocoderStatus.OK) {
                            map.setCenter(result[0].geometry.location);
                            var circle = new google.maps.Circle({
                                map: map,
                                radius: radius * 1000,
                                fillColor: '#FFFFFF',
                                editable: false
                            });
                        }
                    }
                );

                var products = [];
                $('li[id^="marker-"]').each(function () {
                    var item = $(this);
                    var product = {
                        title: item.attr("name"),
                        lat: item.attr("locationX"),
                        lng: item.attr("locationY"),
                        zIndex: Number(item.attr("id").replace("marker-", ""))
                    };
                    products.push(product);
                });


                setMarkers(map, products, 'li#marker-');
            }

            var mapCanvasSmall = document.getElementById("map-canvas-small");

            if (!!mapCanvasSmall) {
                var mapContainer = $("#map-canvas-small");
                var product = {
                    lat: mapContainer.attr("locationX"),
                    lng: mapContainer.attr("locationY")
                };

                var productMapOptions = {
                    zoom: 19,
                    disableDefaultUI: true,
                    zoomControl: true,
                    center: new google.maps.LatLng(product.lat, product.lng),
                    mapTypeId: google.maps.MapTypeId.ROADMAP
                };
                var productMap = new google.maps.Map(mapCanvasSmall, productMapOptions);
                var circleOptions = {
                    strokeColor: "#3c763d",
                    strokeOpacity: 0.8,
                    strokeWeight: 2,
                    fillColor: "#3c763d",
                    fillOpacity: 0.35,
                    map: productMap,
                    center: new google.maps.LatLng(product.lat, product.lng),
                    radius: 10
                };
                var locationCircle = new google.maps.Circle(circleOptions);
            }
        };

        function load_google_maps() {
            var script = document.createElement("script");
            script.type = "text/javascript";
            script.src = "http://maps.googleapis.com/maps/api/js?sensor=false&libraries=places&language=fr&callback=google_maps_loaded";
            document.body.appendChild(script);
        }

        function zoom(radius) {
            if (radius <= 0.5)
                return 14;
            if (radius <= 1)
                return 13;
            if (radius <= 3)
                return 12;
            if (radius <= 6)
                return 11;
            if (radius <= 15)
                return 10;
            if (radius <= 25)
                return 9;
            if (radius <= 100)
                return 7;
            if (radius <= 200)
                return 6;
            if (radius <= 300)
                return 5;
            if (radius <= 700)
                return 4;
            return 3;
        }

        function setMarkers(map, locations, markerId) {
            for (var i = 0; i < locations.length; i++) {
                var product = locations[i];

                var image, image_hover;

                if (markerId == "li#marker-") {
                    image = new google.maps.MarkerImage('/static/images/markers.png',
                        new google.maps.Size(20, 33),
                        new google.maps.Point(44, 34 * i),
                        new google.maps.Point(10, 33));

                    image_hover = new google.maps.MarkerImage('/static/images/markers.png',
                        new google.maps.Size(20, 33),
                        new google.maps.Point(0, 34 * i),
                        new google.maps.Point(10, 33));
                }

                var myLatLng = new google.maps.LatLng(product.lat, product.lng);

                var marker = new google.maps.Marker({
                    position: myLatLng,
                    map: map,
                    title: product.title,
                    zIndex: product.zIndex,
                    icon: image
                });

                marker.set("myZIndex", marker.getZIndex());

                google.maps.event.addListener(marker, "mouseover", mouseOverListenerGenerator(image_hover, marker, markerId));
                google.maps.event.addListener(marker, "click", mouseClickListenerGenerator(marker, markerId));
                google.maps.event.addListener(marker, "mouseout", mouseOutListenerGenerator(image, marker, markerId));

                $(markerId + marker.get("myZIndex")).mouseover(triggerMouseOverGenerator(marker));

                $(markerId + marker.get("myZIndex")).mouseout(triggerMouseOutGenerator(marker));
            }
        }

        function mouseClickListenerGenerator(marker, markerId) {
            return function () {
                // Jump to product item
                $('html, body').animate({
                    scrollTop: $(markerId + marker.get("myZIndex")).offset().top - 20
                }, 1000);
            }
        }

        function mouseOverListenerGenerator(image_hover, marker, markerId) {
            return function () {
                console.log("over");
                this.setOptions({
                    icon: image_hover,
                    zIndex: 200
                });

                //TODO: toggle ":hover" styles
//                $(markerId + marker.get("myZIndex")).find(".declarer-container")[0].trigger("hover");
            }
        }

        function mouseOutListenerGenerator(image, marker, markerId) {
            return function () {
                this.setOptions({
                    icon: image,
                    zIndex: this.get("myZIndex")
                });
                $(markerId + marker.get("myZIndex")).removeAttr("style");
            }
        }

        function triggerMouseOverGenerator(marker) {
            return function () {
                marker.setAnimation(google.maps.Animation.BOUNCE);
            }
        }

        function triggerMouseOutGenerator(marker) {
            return function () {
                marker.setAnimation(null);
                google.maps.event.trigger(marker, 'mouseout');
            }
        }

        load_google_maps();
    });
});