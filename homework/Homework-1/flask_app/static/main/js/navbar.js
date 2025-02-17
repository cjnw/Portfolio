document.addEventListener("DOMContentLoaded", function () {
    // Watch for when hamburger menu is clicked 
    const menuIcon = document.querySelector(".menu-icon");
    const navLinks = document.querySelector(".nav-links");

    menuIcon.addEventListener("click", function () {
        navLinks.classList.toggle("active");
    });
});
