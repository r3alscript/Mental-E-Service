const ITEMS_PER_PAGE = 4;
let currentPage = 1;

let selectedPsyID = null;
let selectedTime = null;

function renderPsychologists() {
    const grid = document.getElementById("psychologistsGrid");
    grid.innerHTML = "";

    const start = (currentPage - 1) * ITEMS_PER_PAGE;
    const end = start + ITEMS_PER_PAGE;
    const pageItems = psychologists.slice(start, end);

    pageItems.forEach(p => {
        grid.innerHTML += `
            <div class="psychologist-card">
                <div class="psychologist-main">

                    <div class="psychologist-photo">
                        <img src="${p.avatar_url}" class="psychologist-avatar">
                    </div>

                    <div class="psychologist-details">

                        <div class="info-row first-row">
                            <h3 class="psychologist-name">${p.first_name} ${p.last_name}</h3>
                            <div class="rating-section">
                                <img src="/static/psychologists/media/smiling-face.svg" class="info-icon">
                                <span class="rating-value">${p.rating} / 5.0</span>
                            </div>
                        </div>

                        <div class="info-row second-row">
                            <div class="experience" style="color:#009141; font-weight:300; font-size: 14px;">
                                ${p.experience} років стажу
                            </div>

                            <div class="cancellation">
                                <i class="fa-solid fa-clock-rotate-left info-icon"></i>
                                ${
                                    p.cancel_policy === "24_hours"
                                        ? "Скасування за 24 години"
                                        : p.cancel_policy === "12_hours"
                                        ? "Скасування за 12 годин"
                                        : "Скасування за 6 годин"
                                }
                            </div>
                        </div>

                        <div class="info-row third-row">
                            <div class="price-section">
                                <img src="/static/psychologists/media/funds.svg" class="info-icon">
                                <span class="price">${p.price} ₴</span>
                            </div>

                            <div class="languages">
                                <img src="/static/psychologists/media/group.svg" class="info-icon">
                                ${p.language}
                            </div>
                        </div>

                        <div class="actions-row-card">
                            <button class="action-btn-card book-btn" onclick="openBookingModal(${p.id})">
                                Забронювати
                            </button>

                            <button class="action-btn-card message-btn" onclick="startChat(${p.id})">
                                Написати
                            </button>
                        </div>

                    </div>
                </div>
            </div>
        `;
    });
}

function renderPagination() {
    const pagination = document.getElementById("pagination");
    pagination.innerHTML = "";

    const totalPages = Math.ceil(psychologists.length / ITEMS_PER_PAGE);

    pagination.innerHTML += `
        <span class="pag-arrow ${currentPage === 1 ? 'disabled' : ''}" onclick="changePage(${currentPage - 1})">
            <i class="fa-solid fa-arrow-left"></i>
        </span>
    `;

    for (let i = 1; i <= totalPages; i++) {
        pagination.innerHTML += `
            <span class="pag-page ${currentPage === i ? 'active' : ''}" onclick="changePage(${i})">${i}</span>
        `;
    }

    pagination.innerHTML += `
        <span class="pag-arrow ${currentPage === totalPages ? 'disabled' : ''}" onclick="changePage(${currentPage + 1})">
            <i class="fa-solid fa-arrow-right"></i>
        </span>
    `;
}

function changePage(page) {
    const totalPages = Math.ceil(psychologists.length / ITEMS_PER_PAGE);
    if (page < 1 || page > totalPages) return;

    currentPage = page;
    renderPsychologists();
    renderPagination();
}

renderPsychologists();
renderPagination();
const modal = document.getElementById("bookingModal");
const dateInput = document.getElementById("bookingDate");
const timeSlots = document.getElementById("timeSlots");

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

if (!window.csrftoken) {
    window.csrftoken = getCookie("csrftoken");
}

document.getElementById("closeBooking").onclick = () => {
    modal.classList.remove("open");
    selectedTime = null;
    timeSlots.innerHTML = "";
    timeSlots.classList.add("disabled");
};

function openBookingModal(psychologistId) {
    selectedPsyID = psychologistId;
    modal.classList.add("open");

    selectedTime = null;
    dateInput.value = "";
    timeSlots.classList.add("disabled");
    timeSlots.innerHTML = "";
    const psycho = psychologists.find(p => p.id === psychologistId);

    if (!psycho || !psycho.work_time) {
        timeSlots.innerHTML = `<div style="color:#777;">Графік не вказано</div>`;
        return;
    }

    const [start, end] = psycho.work_time.replace(" ", "").split("-");
    const slots = generateSlots(start, end);
    slots.forEach(t => {
        const btn = document.createElement("button");
        btn.className = "time-slot";
        btn.innerText = t;
        timeSlots.appendChild(btn);
    });
}

function generateSlots(startTime, endTime) {
    const slots = [];
    let [h] = startTime.split(":").map(Number);
    const [endH] = endTime.split(":").map(Number);

    while (h < endH) {
        slots.push(`${String(h).padStart(2, "0")}:00`);
        h++;
    }
    return slots;
}

dateInput.addEventListener("change", () => {
    if (!selectedPsyID) return;

    timeSlots.classList.add("disabled");
    selectedTime = null;

    fetch(`/booking/free-times/${selectedPsyID}/?date=${dateInput.value}`)
        .then(r => r.json())
        .then(data => {
            if (!data.free_times || data.free_times.length === 0) {
                timeSlots.innerHTML = `<div style="margin-top:8px; color:#777; font-size:14px;">
                    Немає вільних слотів на цю дату
                </div>`;
                return;
            }

            timeSlots.classList.remove("disabled");
            timeSlots.innerHTML = "";

            data.free_times.forEach(t => {
                const btn = document.createElement("button");
                btn.className = "time-slot";
                btn.innerText = t;

                btn.onclick = () => {
                    if (timeSlots.classList.contains("disabled")) return;

                    document.querySelectorAll(".time-slot")
                        .forEach(b => b.classList.remove("selected"));

                    btn.classList.add("selected");
                    selectedTime = t;
                };

                timeSlots.appendChild(btn);
            });
        });
});

confirmBooking.onclick = () => {
    if (!selectedPsyID || !selectedTime || !bookingDate.value) return;

    const formData = new FormData();
    formData.append("date", bookingDate.value);
    formData.append("time", selectedTime);

    fetch(`/booking/create/${selectedPsyID}/`, {
        method: "POST",
        body: formData,
        headers: { "X-CSRFToken": getCookie("csrftoken") }
    })
    .then(r => r.json())
    .then(data => {
        if (data.message === "exists") {
            showFloatingAlert("Цей час уже зайнятий!", "error");
            return;
        }
        if (data.message === "ok") {
            showFloatingAlert("Ваш запит надіслано!", "success");
            modal.classList.remove("open");
        }
    })
    .catch(() => {
        showFloatingAlert("Помилка з'єднання!", "error");
    });
};

function startChat(psychologistId) {
    window.location.href = `/chat/start/${psychologistId}/`;
}

function showFloatingAlert(text, type) {
    const box = document.createElement("div");
    box.className = `floating-alert floating-${type}`;
    box.textContent = text;

    document.body.appendChild(box);

    setTimeout(() => {
        box.classList.add("show");
    }, 50);

    setTimeout(() => {
        box.classList.remove("show");
        setTimeout(() => box.remove(), 300);
    }, 3000);
}
