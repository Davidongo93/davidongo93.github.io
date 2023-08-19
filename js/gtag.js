window.addEventListener('load', function() {
  try {
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-5Q8HLX9RJ1');

    console.log("Welcome dev...");
  } catch (error) {
    console.error("An error occurred:", error);
  }
});

script.addEventListener('error', function(event) {
  console.error("Error loading Google Tag Manager script:", event);
});
