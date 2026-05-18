(function () {
  var inbound = new URLSearchParams(window.location.search);
  var passthroughKeys = [
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_content",
    "utm_term",
    "utm_id",
    "distribution_rail",
    "platform",
    "source_post"
  ];

  document.querySelectorAll('a[href*="withreed.com"]').forEach(function (anchor) {
    var url = new URL(anchor.href);
    passthroughKeys.forEach(function (key) {
      if (inbound.has(key)) {
        url.searchParams.set(key, inbound.get(key));
      }
    });
    url.searchParams.set("landing_page", window.location.pathname);
    anchor.href = url.toString();
  });
})();
