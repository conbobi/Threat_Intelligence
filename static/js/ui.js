document.addEventListener("DOMContentLoaded", function () {
    const dropdowns = document.querySelectorAll(".user-hover-dropdown");

    dropdowns.forEach(function (dropdown) {
        const menu = dropdown.querySelector(".dropdown-menu");

        if (!menu) return;

        dropdown.addEventListener("mouseenter", function () {
            menu.classList.add("show");
        });

        dropdown.addEventListener("mouseleave", function () {
            menu.classList.remove("show");
        });
    });
});