import asyncio
from linebot.v3.messaging import AsyncApiClient, AsyncMessagingApi, ReplyMessageRequest, TextMessage, Configuration
from linebot.v3 import WebhookParser
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from app.api import deps
from app.models import LineUser
from app.enum.province import Province
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from linebot.exceptions import InvalidSignatureError
from app.core.config import get_settings


class LineMessageHandler:
    def __init__(self):
        settings = get_settings()
        self.configuration = Configuration(access_token=settings.line.channel_access_token)
        self.api_client = AsyncApiClient(configuration=self.configuration)
        self.messaging_api = AsyncMessagingApi(self.api_client)
        self.parser = WebhookParser(channel_secret=settings.line.channel_secret)
        self.user_states = {}  # Temporary in-memory state

    async def handle(self, body: str, signature: str):
        events = self.parser.parse(body, signature)
        async with deps.get_session() as session:
            tasks = [
                self._process_event(event, session)
                for event in events
                if isinstance(event, MessageEvent) and isinstance(event.message, TextMessageContent)
            ]
            await asyncio.gather(*tasks)

    async def _process_event(self, event: MessageEvent, session: AsyncSession):
        user_id = event.source.user_id
        received_text = event.message.text.strip()

        # Check state
        if self.user_states.get(user_id) == "setting_province":
            await self._handle_province_setting(user_id, received_text, event.reply_token, session)
        elif received_text == "ตั้งค่า":
            self.user_states[user_id] = "setting_province"
            await self.messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="คุณมาจากจังหวัดอะไร? กรุณาพิมพ์ชื่อจังหวัด (ภาษาไทยหรือภาษาอังกฤษ)")],
                )
            )
        else:
            await self.messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=f"ได้รับข้อความ: {received_text}")],
                )
            )

    async def _handle_province_setting(self, user_id: str, received_text: str, reply_token: str, session: AsyncSession):
        matched_province = next(
            (
                province
                for province in Province
                if province.value.name_th == received_text or province.value.name_en == received_text
            ),
            None,
        )
        if matched_province:
            success_message = await self._update_user_province(session, user_id, matched_province.value.name_th)
            await self.messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=[TextMessage(text=success_message)],
                )
            )
        else:
            await self.messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=[TextMessage(text="ชื่อจังหวัดไม่ถูกต้อง กรุณาลองใหม่.")],
                )
            )
        self.user_states.pop(user_id, None)  # Reset state

    async def _update_user_province(self, session: AsyncSession, user_id: str, province_name: str) -> str:
        result = await session.execute(select(LineUser).where(LineUser.user_id == user_id))
        line_user = result.scalars().first()
        if line_user:
            line_user.province = province_name
            session.add(line_user)
            await session.commit()
            return f"ตั้งค่าเสร็จสิ้น: {province_name}"
        return "ไม่พบผู้ใช้ในระบบฐานข้อมูล"


message_handler = LineMessageHandler()
