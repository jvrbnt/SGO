function googleTranslateElementInit() {
    new google.translate.TranslateElement({pageLanguage: 'en', includedLanguages: 'en,es', autoDisplay: false}, 'google_translate_element');
}

function changeLanguage(langCode) {
    if (langCode === 'en') {
        document.cookie = "googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
        document.cookie = "googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; domain=" + location.hostname + "; path=/;";
    } else {
        document.cookie = "googtrans=/en/" + langCode + "; expires=Thu, 01 Jan 2030 00:00:00 UTC; path=/;";
        document.cookie = "googtrans=/en/" + langCode + "; expires=Thu, 01 Jan 2030 00:00:00 UTC; domain=" + location.hostname + "; path=/;";
    }
    location.reload();
}
