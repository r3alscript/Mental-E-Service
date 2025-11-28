document.addEventListener("DOMContentLoaded", () => {

    document.querySelectorAll(".select-wrapper select").forEach(select => {
        const wrapper = select.closest(".select-wrapper");

        select.addEventListener("click", () => {
            wrapper.classList.toggle("open");
        });

        select.addEventListener("blur", () => {
            wrapper.classList.remove("open");
        });
    });
});

function startPhone(input) {
    if (input.value.trim() === "") {
        input.value = "+380";
    }
}

function formatPhone(input) {
    let value = input.value.replace(/[^\d]/g, "");

    if (!value.startsWith("380")) {
        value = "380" + value;
    }

    value = "+380" + value.substring(3, 12);

    input.value = value;
}