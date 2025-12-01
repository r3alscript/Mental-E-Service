import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Dialog, Message

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.dialog_id = int(self.scope["url_route"]["kwargs"]["dialog_id"])
        self.room_group = f"chat_{self.dialog_id}"
        self.user = self.scope["user"]

        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        text = (data.get("text") or "").strip()
        if not text:
            return

        dialog_id = int(data["dialog_id"])
        sender_id = int(data["sender_id"])

        msg_data = await self.create_message(dialog_id, sender_id, text)

        await self.channel_layer.group_send(
            self.room_group,
            {
                "type": "chat_message",
                **msg_data,
            },
        )

        await self.send_chat_list_update(dialog_id, msg_data)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def create_message(self, dialog_id, sender_id, text):
        dialog = Dialog.objects.get(id=dialog_id)
        sender = User.objects.get(id=sender_id)

        msg = Message.objects.create(
            dialog=dialog,
            sender=sender,
            text=text,
            is_read=False
        )

        local_time = timezone.localtime(msg.created_at)

        return {
            "id": msg.id,
            "sender_id": msg.sender_id,
            "text": msg.text,
            "created_at": local_time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    async def send_chat_list_update(self, dialog_id, msg_data):
        dialog = await database_sync_to_async(Dialog.objects.get)(id=dialog_id)

        client_id = dialog.client_id
        psychologist_id = dialog.psychologist_id

        for uid in [client_id, psychologist_id]:
            unread = 1 if uid != msg_data["sender_id"] else 0

            await self.channel_layer.group_send(
                f"chat_list_{uid}",
                {
                    "type": "chat_list_update",
                    "dialog_id": dialog_id,
                    "text": msg_data["text"],
                    "created_at": msg_data["created_at"],
                    "sender_id": msg_data["sender_id"],
                    "unread_count": unread,
                },
            )

            await self.channel_layer.group_send(
                f"chat_sidebar_{uid}",
                {
                    "type": "chat_sidebar_update",
                    "has_unread": unread > 0
                }
            )

    @database_sync_to_async
    def get_unread_count(self, dialog, user_id):
        return dialog.messages.filter(is_read=False).exclude(sender_id=user_id).count()


class ChatListConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.group_name = f"chat_list_{self.user.id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def chat_list_update(self, event):
        await self.send(text_data=json.dumps(event))

class ChatSidebarConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.group_name = f"chat_sidebar_{self.user.id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def chat_sidebar_update(self, event):
        await self.send(text_data=json.dumps(event))
