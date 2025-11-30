document.addEventListener("DOMContentLoaded", function () {
    const currentUrl = window.location.pathname;
    const navItems = document.querySelectorAll(".nav-item");

    navItems.forEach(item => {
        const urlKey = item.dataset.url;

        const icon = item.querySelector(".nav-icon");
        if (icon && !icon.dataset.defaultIcon) {
            icon.dataset.defaultIcon = icon.src;
        }

        if (urlKey && currentUrl.startsWith(urlKey)) {
            item.classList.add("active");

            if (icon && icon.dataset.activeIcon) {
                icon.src = icon.dataset.activeIcon;
            }
        }
    });

    const submenuParent = document.querySelector('.nav-item .has-submenu');
    if (submenuParent) {
        const parentItem = submenuParent.closest('.nav-item');
        const submenu = parentItem.querySelector('.submenu');

        submenuParent.addEventListener('click', function (e) {
            e.preventDefault();

            parentItem.classList.toggle('open');
            submenu.classList.toggle('open');
        });
    }
});
