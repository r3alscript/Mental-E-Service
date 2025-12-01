const dialogId = CHAT_DIALOG_ID;
const userId = Number(CURRENT_USER_ID);

const protocol = window.location.protocol === "https:" ? "wss" : "ws";

const chatSocket = new WebSocket(
    protocol + "://" + window.location.host + "/ws/chat/" + dialogId + "/"
);

const messagesDiv = document.getElementById("messages");

let lastMessageDate = null;

function formatUaDate(dateObj) {
    const MONTHS = [
        "січня","лютого","березня","квітня","травня","червня",
        "липня","серпня","вересня","жовтня","листопада","грудня"
    ];
    return `${dateObj.getDate()} ${MONTHS[dateObj.getMonth()]}`;
}

function addDateSeparatorIfNeeded(dateStr) {
    if (lastMessageDate === dateStr) return;

    const d = new Date(dateStr);

    const wrapper = document.createElement("div");
    wrapper.className = "date-wrapper";

    const div = document.createElement("div");
    div.className = "message-date";
    div.textContent = formatUaDate(d);

    wrapper.appendChild(div);
    messagesDiv.appendChild(wrapper);

    lastMessageDate = dateStr;
}

const input = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");

sendBtn.addEventListener("click", sendMessage);

input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

function sendMessage() {
    const text = input.value.trim();
    if (!text) return;

    chatSocket.send(
        JSON.stringify({
            type: "chat_message",
            text: text,
            dialog_id: dialogId,
            sender_id: userId
        })
    );

    input.value = "";
}

chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);

    const created = data.created_at;                
    const [dateKey, timeFull] = created.split(" ");  
    const timeStr = timeFull.substring(0, 5);        

    addDateSeparatorIfNeeded(dateKey);

    const isMe = data.sender_id === userId;

    addMessageToUI(data.text, timeStr, isMe);
};

function addMessageToUI(text, timeStr, isMe) {
    const row = document.createElement("div");
    row.className = "message-row " + (isMe ? "me" : "them");

    const avatar = document.createElement("img");
    avatar.className = "msg-avatar " + (isMe ? "right" : "left");
    avatar.src = isMe ? window.MY_AVATAR : window.OTHER_AVATAR;

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";
    bubble.textContent = text;

    const time = document.createElement("div");
    time.className = "message-time";
    time.textContent = timeStr;

    bubble.appendChild(time);

    if (isMe) {
        row.appendChild(bubble);
        row.appendChild(avatar);
    } else {
        row.appendChild(avatar);
        row.appendChild(bubble);
    }

    messagesDiv.appendChild(row);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

document.addEventListener("DOMContentLoaded", () => {
    const dateElems = messagesDiv.querySelectorAll(".message-date");

    if (dateElems.length > 0) {
        const lastLabel = dateElems[dateElems.length - 1].textContent.trim();

        const MONTHS = {
            "січня":1, "лютого":2, "березня":3, "квітня":4, "травня":5, "червня":6,
            "липня":7, "серпня":8, "вересня":9, "жовтня":10, "листопада":11, "грудня":12
        };

        const [day, monthName] = lastLabel.split(" ");
        const month = MONTHS[monthName];
        const year = new Date().getFullYear();

        lastMessageDate = `${year}-${String(month).padStart(2,"0")}-${String(day).padStart(2,"0")}`;
    }
});
