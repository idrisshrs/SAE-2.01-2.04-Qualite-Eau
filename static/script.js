// Script JS pour le menu responsive

// Variables pour le menu
const menuBtn = document.querySelector('.menu-btn');
const menuItems = document.querySelector('.menu-items');
const menuIcon = menuBtn.querySelector('.material-icons');

// Écouteur d'événement pour le clic sur le bouton de menu
menuBtn.addEventListener('click', () => {
    // Affiche/masque les éléments du menu
    menuItems.classList.toggle('show');
    // Change l'icône du bouton de menu
    if (menuItems.classList.contains('show')) {
        menuIcon.textContent = 'close';
    } else {
        menuIcon.textContent = 'menu';
    }
});

// Script JS pour la barre de filtres

// Variables pour la barre de filtres
const filterToggle = document.getElementById('filter-toggle');
const filterBar = document.getElementById('filter-bar');
const filterArrow = filterToggle ? filterToggle.querySelector('.filter-arrow') : null;

// Écouteur d'événement pour le clic sur le bouton de filtre
if (filterToggle && filterBar && filterArrow) {
    // Affiche/masque la barre de filtres et fait pivoter la flèche
    filterToggle.addEventListener('click', () => {
        filterBar.classList.toggle('show');
        filterArrow.classList.toggle('rotated');
    });
}