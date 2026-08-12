/**
 * Initialisation immédiate du thème (Mode sombre/clair)
 * Placé en dehors du DOMContentLoaded pour s'exécuter au plus vite et éviter le flash visuel.
 */
(function initTheme() {
    const savedTheme = localStorage.getItem('theme');
    const htmlElement = document.documentElement;

    if (savedTheme === 'dark') {
        htmlElement.classList.add('dark-theme');
    } else if (savedTheme === 'light') {
        htmlElement.classList.add('light-theme');
    }
})();


// GESTION DES ÉVÉNEMENTS : Attend que le HTML soit totalement chargé
document.addEventListener('DOMContentLoaded', function() {

    // Module : Clic extérieur pour fermer le sélecteur de langue
    initLanguageDropdownCloser();

    // Module : Gestion du clic pour le switch de thème
    initThemeSwitcher();

});

/**
 * MODULE : Gestion du clic extérieur pour fermer le sélecteur de langue
 */
function initLanguageDropdownCloser() {
    document.addEventListener('click', function(event) {
        const langDetails = document.querySelector('.lang-dropdown-details');

        // Si le menu est ouvert ET que le clic a eu lieu à l'extérieur
        if (langDetails && langDetails.open && !langDetails.contains(event.target)) {
            langDetails.open = false;
        }
    });
}

/**
 * MODULE : Gestion du basculement de thème au clic sur le bouton dédié
 */
function initThemeSwitcher() {
    const themeBtn = document.querySelector('.lightdark-theme');
    if (!themeBtn) return; // Sécurité si le bouton n'existe pas sur la page

    themeBtn.addEventListener('click', function() {
        const isSystemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const htmlElement = document.documentElement; // On cible <html> pour rester cohérent avec l'init

        if (htmlElement.classList.contains('dark-theme')) {
            htmlElement.classList.replace('dark-theme', 'light-theme');
            localStorage.setItem('theme', 'light');
        } else if (htmlElement.classList.contains('light-theme')) {
            htmlElement.classList.replace('light-theme', 'dark-theme');
            localStorage.setItem('theme', 'dark');
        } else {
            // Premier clic : aucune classe n'est encore posée
            if (isSystemDark) {
                htmlElement.classList.add('light-theme');
                localStorage.setItem('theme', 'light');
            } else {
                htmlElement.classList.add('dark-theme');
                localStorage.setItem('theme', 'dark');
            }
        }
    });
}

/**
 * Soumet le formulaire Django de changement de langue
 * @param {string} langCode - Le code de la langue (ex: 'fr', 'en')
 */
function submitLanguage(langCode) {
    const langInput = document.getElementById('lang-input');
    const langForm = document.getElementById('lang-form');

    if (langInput && langForm) {
        langInput.value = langCode;
        langForm.submit();
    }
}
