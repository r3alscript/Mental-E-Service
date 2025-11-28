document.addEventListener("DOMContentLoaded", () => {

    const personalBlock = document.getElementById("personalBlock");
    const personalEditBtn = document.querySelector(".personal-edit-btn");

    if (personalBlock && personalEditBtn) {
        initEditableBlock(personalBlock, personalEditBtn, ".editable", "/profile/update_personal/", true);
    }

    const workspaceBlock = document.getElementById("workspaceBlock");
    const workspaceEditBtn = document.querySelector(".workspace-edit-btn");

    if (workspaceBlock && workspaceEditBtn) {
        initEditableBlock(workspaceBlock, workspaceEditBtn, ".editable-w", "/profile/update_workspace/", false);
    }

    const changePassBtn = document.getElementById("changePasswordBtn");
    if (changePassBtn) {
        changePassBtn.addEventListener("click", (e) => {
            e.preventDefault();
            openPasswordModal();
        });
    }

    const deleteBtn = document.getElementById("deleteAccountBtn");

    if (deleteBtn) {
        deleteBtn.addEventListener("click", (e) => {
            e.preventDefault();
            openDeleteModal();
        });
    }

    const confirmDelete = document.getElementById("confirmDeleteBtn");
    if (confirmDelete) {
        confirmDelete.addEventListener("click", () => {
            window.location.href = document
                .getElementById("deleteAccountBtn")
                .getAttribute("href");
        });
    }

    const avatar = document.getElementById("avatarPreview");
    const avatarInput = document.getElementById("avatarInput");

    if (avatar && avatarInput) {
        avatar.addEventListener("click", () => {
            avatarInput.click();
        });

        avatarInput.addEventListener("change", () => {
            const file = avatarInput.files[0];
            if (!file) return;

            const formData = new FormData();
            formData.append("avatar", file);

            fetch("/profile/upload_avatar/", {
                method: "POST",
                headers: { "X-CSRFToken": getCSRFToken() },
                body: formData
            })
                .then(r => r.json())
                .then(d => {
                    if (d.success) avatar.src = d.url;
                    else alert(d.error || "Помилка завантаження");
                });
        });
    }
});


function normalizeWorkspaceField(field, value) {
    if (field === "experience") return value.replace(/\D+/g, "");
    if (field === "price") return value.replace(/[^0-9.]/g, "");
    if (field === "cancel_policy") {
        const map = {
            "За 24 години": "24_hours",
            "За 12 годин": "12_hours",
            "За 6 годин": "6_hours"
        };
        return map[value] || "";
    }
    return value;
}


function initEditableBlock(block, button, selector, updateUrl, isPersonal) {
    let editMode = false;

    button.addEventListener("click", (e) => {
        e.preventDefault();
        const fields = block.querySelectorAll(selector);

        if (!editMode) {
            fields.forEach(field => {
                const fieldName = field.dataset.field;
                const value = field.innerText.trim();
                let input;

                if (fieldName === "work_time") {
                    const [start, end] = value.split("-");

                    const wrap = document.createElement("div");
                    wrap.classList.add("worktime-wrapper");

                    const fromLabel = document.createElement("span");
                    fromLabel.classList.add("worktime-label");
                    fromLabel.innerText = "з";

                    const toLabel = document.createElement("span");
                    toLabel.classList.add("worktime-label");
                    toLabel.innerText = "до";

                    const startSelect = document.createElement("select");
                    const endSelect = document.createElement("select");

                    startSelect.dataset.field = "work_time_start";
                    endSelect.dataset.field = "work_time_end";

                    startSelect.classList.add("edit-input", "time-select");
                    endSelect.classList.add("edit-input", "time-select");

                    for (let h = 6; h <= 20; h++) {
                        let hh = h.toString().padStart(2, "0") + ":00";
                        const opt = document.createElement("option");
                        opt.value = hh;
                        opt.innerText = hh;
                        if (hh === start) opt.selected = true;
                        startSelect.appendChild(opt);
                    }

                    for (let h = 8; h <= 22; h++) {
                        let hh = h.toString().padStart(2, "0") + ":00";
                        const opt = document.createElement("option");
                        opt.value = hh;
                        opt.innerText = hh;
                        if (hh === end) opt.selected = true;
                        endSelect.appendChild(opt);
                    }

                    wrap.appendChild(fromLabel);
                    wrap.appendChild(startSelect);
                    wrap.appendChild(toLabel);
                    wrap.appendChild(endSelect);

                    field.replaceWith(wrap);
                    return;
                }

                if (fieldName === "about") input = document.createElement("textarea");
                else if (fieldName === "birth_date") {
                    input = document.createElement("input");
                    input.type = "date";
                    const parsed = new Date(value);
                    if (!isNaN(parsed)) input.value = parsed.toISOString().slice(0, 10);
                } else {
                    input = document.createElement("input");
                    input.type = "text";
                    input.value = value;
                }

                input.dataset.field = fieldName;
                input.classList.add("edit-input");
                field.replaceWith(input);
            });

            button.innerHTML = "Зберегти";
            button.classList.add("save-btn");
            editMode = true;
        }

        else {
            const inputs = block.querySelectorAll(".edit-input, select");
            let updatedData = {};

            let workStart = null;
            let workEnd = null;

            inputs.forEach(input => {
                const fieldName = input.dataset.field;

                if (fieldName === "work_time_start") {
                    workStart = input.value;
                    return;
                }

                if (fieldName === "work_time_end") {
                    workEnd = input.value;
                    return;
                }

                const newElement = fieldName === "about"
                    ? document.createElement("p")
                    : document.createElement("span");

                newElement.classList.add("value", selector.replace(".", ""));
                newElement.dataset.field = fieldName;
                newElement.innerText = input.value;

                updatedData[fieldName] = isPersonal
                    ? input.value
                    : normalizeWorkspaceField(fieldName, input.value);

                input.replaceWith(newElement);
            });

            if (workStart && workEnd) {
                updatedData["work_time"] = `${workStart}-${workEnd}`;

                const span = document.createElement("span");
                span.classList.add("value", selector.replace(".", ""));
                span.dataset.field = "work_time";
                span.innerText = `${workStart}-${workEnd}`;

                const oldWrap = block.querySelector(".worktime-wrapper");
                if (oldWrap) oldWrap.replaceWith(span);
            }

            button.innerHTML = `
                <img src="/static/profiles/media/edit.svg" class="edit-icon">
                Редагувати
            `;
            button.classList.remove("save-btn");

            fetch(updateUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken()
                },
                body: JSON.stringify(updatedData)
            });

            editMode = false;
        }
    });
}


function openPasswordModal() {
    document.getElementById("passwordModal").style.display = "flex";
}

function closePasswordModal() {
    document.getElementById("passwordModal").style.display = "none";
}
async function submitPasswordChange() {
    const oldPassword = document.getElementById("oldPassword").value.trim();
    const newPassword = document.getElementById("newPassword").value.trim();

    if (!oldPassword || !newPassword) {
        alert("Заповніть всі поля");
        return;
    }

    const response = await fetch("/profile/change-password/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify({
            old_password: oldPassword,
            new_password: newPassword
        })
    });

    const data = await response.json();

    if (data.error) {
        alert(data.error);
        return;
    }

    alert("Пароль успішно змінено!");
    closePasswordModal();
}


function getCSRFToken() {
    const name = "csrftoken=";
    const cookies = decodeURIComponent(document.cookie).split(";");

    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name)) return cookie.substring(name.length);
    }
    return "";
}

function openDeleteModal() {
    document.getElementById("deleteModal").style.display = "flex";
}

function closeDeleteModal() {
    document.getElementById("deleteModal").style.display = "none";
}

