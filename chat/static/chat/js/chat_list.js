const protocol = location.protocol === "https:" ? "wss" : "ws";
const listSocket = new WebSocket(protocol + "://" + location.host + "/ws/chat/list/");

listSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    if (data.type !== "chat_list_update") return;

    const dialogId = data.dialog_id;
    const item = document.querySelector(`.dialog-item[data-id="${dialogId}"]`);
    if (!item) return;

    item.querySelector(".dialog-last").textContent = data.text;

    const timeDiv = item.querySelector(".dialog-time");
    const d = new Date(data.created_at); 
    timeDiv.textContent = d.toLocaleTimeString("uk-UA", {
        hour: "2-digit",
        minute: "2-digit"
    });

    const dot = item.querySelector(".dialog-unread-dot");

    if (data.unread_count > 0) {
        dot.style.display = "block";
    } else {
        dot.style.display = "none";
    }
};
