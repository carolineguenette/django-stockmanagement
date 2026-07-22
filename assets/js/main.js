// Attend que le DOM (HTML) soit totalement chargé
document.addEventListener('DOMContentLoaded', function() {

    document.addEventListener('click', function(event) {
        const langDetails = document.querySelector('.lang-dropdown-details');

        // Si le menu est actuellement ouvert ET que le clic a eu lieu à l'extérieur du composant
        if (langDetails && langDetails.open && !langDetails.contains(event.target)) {
            // Fermeture propre et native
            langDetails.open = false;
        }
    });

});