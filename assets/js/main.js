// Attend que le DOM (HTML) soit totalement chargé
document.addEventListener('DOMContentLoaded', function() {

    document.addEventListener('click', function(event) {
        const dropdown = document.querySelector('.lang-dropdown');

        // Si le dropdown existe et que le clic est à l'extérieur
        if (dropdown && !dropdown.contains(event.target)) {
            dropdown.removeAttribute('open');
        }
    });

});
