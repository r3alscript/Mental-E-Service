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

    const protocol = location.protocol === "https:" ? "wss" : "ws";
    const socket = new WebSocket(protocol + "://" + location.host + "/ws/chat/sidebar/");

    socket.onmessage = function (e) {
        const data = JSON.parse(e.data);
        if (data.type !== "chat_sidebar_update") return;

        const dot = document.getElementById("chat-unread-dot");
        if (!dot) return;

        if (data.has_unread) {
            dot.style.display = "inline-block";
        } else {
            dot.style.display = "none";
        }
    };
});
