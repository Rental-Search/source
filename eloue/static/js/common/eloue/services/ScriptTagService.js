"use strict";
define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    /**
     * Service for redirection from Go Sport public page to e-loue dashboard app.
     */
    EloueCommon.factory("ScriptTagService", ["$window", "$document", function ($window, $document) {

        var scriptTagService = {};

        /**
         * Push track event to Google Analytics.
         *
         * @param category category
         * @param action action
         * @param value value
         */
        scriptTagService.trackEvent = function (category, action, value) {
            _gaq.push(["_trackEvent", category, action, value]);
        };

        /**
         * Push track page view to Google Analytics.
         */
        scriptTagService.trackPageView = function () {
            _gaq.push(["_trackPageview", $window.location.href + "/success/"]);
        };

        /**
         * Add Google ad scripts.
         */
        scriptTagService.loadAdWordsTags = function (googleConversionLabel) {
            $window.google_trackConversion({
                google_conversion_id: 1027691277,
                google_conversion_language: "en",
                google_conversion_format: "3",
                google_conversion_color: "ffffff",
                google_conversion_label: googleConversionLabel,
                google_conversion_value: 1.00,
                google_conversion_currency: "EUR",
                google_remarketing_only: false
            });
        };

        /**
         * Add this tags when a user succeeded to post a new product:
         * <script type="text/javascript" src="https://lead.pdltracking.com/?lead_id={{product.owner.pk}}%&tt=javascript&sc=1860"></script>
         <script type="text/javascript" src="https://lead.pdltracking.com/?lead_id={{product.owner.pk}}&tt=javascript&sc=1859"></script>
         <noscript>
         <img src="https://lead.pdltracking.com/?lead_id={{product.owner.pk}}&tt=pixel&sc=1859" width="1" height="1" border="0" />
         </noscript>
         <IMG SRC="https://clic.reussissonsensemble.fr/registersale.asp?site=13625&mode=ppl&ltype=1&order=TRACKING_NUMBER" WIDTH="1" HEIGHT="1" />
         <script type="text/javascript" id="affilinet_advc">
         var type = "Checkout";
         var site = "13625";
         </script>
         <script type="text/javascript" src="https://clic.reussissonsensemble.fr/art/JS/param.aspx"></script>
         <script src="//l.adxcore.com/a/track_conversion.php?annonceurid=21679"></script>
         <noscript>
         <img src="//l.adxcore.com/a/track_conversion.php?adsy=1&annonceurid=21679">
         </noscript>
         */
        scriptTagService.loadPdltrackingScript = function (currentUserId) {

            var script1860 = $document[0].createElement("script");
            script1860.type = "text/javascript";
            script1860.src = "https://lead.pdltracking.com/?lead_id=" + currentUserId + "&tt=javascript&sc=1860";
            $document[0].body.appendChild(script1860);

            var script1859 = $document[0].createElement("script");
            script1859.type = "text/javascript";
            script1859.src = "https://lead.pdltracking.com/?lead_id=" + currentUserId + "%&tt=javascript&sc=1859";
            $document[0].body.appendChild(script1859);

            var noscript1859 = $document[0].createElement("noscript");
            var img1859 = $document.createElement("img");
            img1859.src = "https://lead.pdltracking.com/?lead_id=" + currentUserId + "&tt=pixel&sc=1859";
            img1859.width = "1";
            img1859.height = "1";
            img1859.border = "0";
            noscript1859.appendChild(img1859);
            $document[0].body.appendChild(noscript1859);

            var img13625 = $document[0].createElement("img");
            img13625.src = "https://clic.reussissonsensemble.fr/registersale.asp?site=13625&mode=ppl&ltype=1&order=TRACKING_NUMBER";
            img13625.width = "1";
            img13625.height = "1";
            $document[0].body.appendChild(img13625);

            var scriptAffilinet = $document[0].createElement("script");
            scriptAffilinet.type = "text/javascript";
            scriptAffilinet.id = "affilinet_advc";
            var code = "var type = 'Checkout';" +
                "var site = '13625';";
            try {
                scriptAffilinet.appendChild($document[0].createTextNode(code));
                $document[0].body.appendChild(scriptAffilinet);
            } catch (e) {
                scriptAffilinet.text = code;
                $document[0].body.appendChild(scriptAffilinet);
            }

            //var scriptClic = document.createElement("script");
            //scriptClic.type = "text/javascript";
            //scriptClic.src = "https://clic.reussissonsensemble.fr/art/JS/param.aspx";
            //document.body.appendChild(scriptClic);

            var oldDocumentWrite = $document[0].write;
            // change document.write temporary
            $document[0].write = function (node) {
                $("body").append(node);
            };
            $.getScript("https://clic.reussissonsensemble.fr/art/JS/param.aspx", function () {
                // replace the temp document.write with the original version
                setTimeout(function () {
                    $document[0].write = oldDocumentWrite;
                }, 500);
            });

            var scriptAnnonceur = $document[0].createElement("script");
            scriptAnnonceur.src = "//l.adxcore.com/a/track_conversion.php?annonceurid=21679";
            $document[0].body.appendChild(scriptAnnonceur);

            var noscriptAnnonceur = $document[0].createElement("noscript");
            var imgAnnonceur = $document[0].createElement("img");
            imgAnnonceur.src = "//l.adxcore.com/a/track_conversion.php?adsy=1&annonceurid=21679";
            noscriptAnnonceur.appendChild(imgAnnonceur);
            $document[0].body.appendChild(noscriptAnnonceur);
        };
        return scriptTagService;
    }]);
});
